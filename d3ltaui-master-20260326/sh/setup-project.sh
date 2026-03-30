#!/bin/bash

CRON_PROCESSING_LOG="/var/log/d3ltaui.process.log"
CRON_PROCESSING_TAG="d3ltaui_process_jobs"
CRON_PROCESSING="*/1 * * * * cd /var/www/d3ltaui && bash -c sh/process-jobs.sh >> $CRON_PROCESSING_LOG 2>&1 $CRON_PROCESSING_TAG"

CRON_CLEANUP_LOG="/var/log/d3ltaui.cleanup.log"
CRON_CLEANUP_TAG="d3ltaui_cleanup"
CRON_CLEANUP="*/3 * * * * cd /var/www/d3ltaui && bash -c sh/cleanup-old-jobs.sh >> $CRON_CLEANUP_LOG 2>&1 $CRON_CLEANUP_TAG"

MICROMAMBA_ENV_DIR="/var/micromamba/envs"
MICROMAMBA_ENV="py311"
PROJECT_NAME='d3ltaui'


read_host_info() {
	read -p 'Host name or IP address: ' HOST
	if [[ -z $HOST ]]; then
		echo "[ERROR] Host name can not be empty."
		exit 1
	fi

	read -p 'Port (default: Apache default): ' PORT
}


ensure_python() {
	# Prefer system python3.11
	if command -v python3.11 >/dev/null 2>&1; then
		PYTHON_RUNNER="python3.11"
		return
	fi

	# Try micromamba environment
	if [ -x "$HOME/.local/bin/micromamba" ]; then
		export PATH="$HOME/.local/bin:$PATH"
	fi

	if command -v micromamba >/dev/null 2>&1; then
		if micromamba env list | awk '{print $1}' | grep -q "$MICROMAMBA_ENV"; then
			PYTHON_RUNNER="micromamba run --prefix $MICROMAMBA_ENV_DIR/$MICROMAMBA_ENV python"
			return
		fi
	fi

	echo "[ERROR] Python 3.11 not available. Installation failed."
	exit 1
}


remove_old_installation() {
	if [[ -d $PROJECT_ROOT/$PROJECT_NAME/ ]]; then
		echo "Removing old installation... " \
			&& sudo rm -rf $PROJECT_ROOT/$PROJECT_NAME \
			&& sudo rm -rf $CRON_PROCESSING_LOG \
			&& sudo rm -rf $CRON_CLEANUP_LOG \
			&& echo "OK"
	fi
}


extract_tarball() {
	TARBALL="$PROJECT_NAME.tar.gz"

	if [[ ! -f $TARBALL ]]; then
		echo "Error: Project tarball '$TARBALL' not found in the current directory. Installation failed."
		exit 1
	fi

	# @todo: remove the $PROJECT_ROOT dir first
	printf "Extracting project tarball... " \
		&& sudo mkdir -p $PROJECT_ROOT \
		&& sudo chown -R `whoami` $PROJECT_ROOT \
		&& tar -xzf $TARBALL -C $PROJECT_ROOT \
		&& echo "OK"
}


create_venv() {
	if [[ ! -d $PROJECT_ROOT ]]; then
		echo "Could not find project directory '$PROJECT_ROOT'. Did you extract the tarball first?"
		exit 1
	fi

	previous_dir=`pwd`

	cd $PROJECT_ROOT \
		&& echo "Creating a virtual environment... " \
		&& ([[ -d $ENV_NAME ]] || $PYTHON_RUNNER -m venv "$ENV_NAME") \
		&& source $ENV_NAME/bin/activate \
		&& pip install -r requirements.txt \
		&& pip install mod_wsgi \
		&& deactivate

	cd $previous_dir
}


generate_random_string() {
	local length=67
	LC_ALL=C tr -dc 'A-Za-z0-9!@#$%^&*()_+=-[]{}|;:,.<>?/' < /dev/urandom | head -c "$length"
	echo
}


update_configuration() {
	if [ ! -d $PROJECT_ROOT/$ENV_NAME ]; then
		echo "[ERROR] virtualenv not found in '$PROJECT_ROOT'. Installation failed."
		exit 2
	fi

	previous_dir=`pwd`

	printf 'Updating configuration... ' && \

		# update HOST and PORT
		sed -r -i "s/SITE_HOST\s*=\s*'[^']+'/SITE_HOST = '$HOST'/" $PROJECT_ROOT/$PROJECT_NAME/$PROJECT_NAME/settings.py && \
		sed -r -i "s/SITE_PORT\s*=\s*'[^']+'/SITE_PORT = '$PORT'/" $PROJECT_ROOT/$PROJECT_NAME/$PROJECT_NAME/settings.py && \

		# use the secret from the newly generated settings.py
		escaped_key=$(printf '%s\n' "$(generate_random_string)" | sed 's/[\/&]/\\&/g') && \
		sed -r -i "s/SECRET_KEY\s*=\s*'[^']+'/SECRET_KEY='$escaped_key'/" $PROJECT_ROOT/$PROJECT_NAME/$PROJECT_NAME/settings.py && \

		# change some settings that should not be on production
		# sed -r -i "s/DEBUG\s*=\s*True/DEBUG = False/" $PROJECT_ROOT/$PROJECT_NAME/$PROJECT_NAME/settings.py && \

		echo 'OK'

	printf 'Allowing Apache to access to files... ' && \
		chmod -R +x $PROJECT_ROOT && \
		echo 'OK'

	cd $PROJECT_ROOT && \
		source $ENV_NAME/bin/activate && \
		cd $PROJECT_NAME && \
		./manage.py migrate &&
		deactivate

	cd $previous_dir
}


set_fcontext () {
	local type="$1"
	local path="$2"
	sudo semanage fcontext -m -t "$type" "$path" 2>/dev/null || \
	sudo semanage fcontext -a -t "$type" "$path"
}


setup_apache() {
	cat $PROJECT_ROOT/vhost.conf.sample \
		| sed -r -e "s|domain.com|$HOST|" \
		| sed -r -e "s|\.domain.com|.$HOST|" \
		| sed -r -e "s|/path/to/site|$PROJECT_ROOT/$PROJECT_NAME|" \
		| sed -r -e "s|/path/to/venv|$PROJECT_ROOT/$ENV_NAME|" \
		| sed -r -e "s|project_name|$PROJECT_NAME|" > $PROJECT_ROOT/vhost.conf

	if ! [[ -z $PORT ]]; then
		sed -i "s/:80>/:$PORT>/" $PROJECT_ROOT/vhost.conf
	fi

	if [[ $HOST =~ ^[0-9]{1,3}\.[0-9]{1,3}\. ]]; then
		sed -i -r s/[[:space:]]*ServerAlias[^\n]+// $PROJECT_ROOT/vhost.conf
	fi

	sudo mv $PROJECT_ROOT/vhost.conf /etc/httpd/conf.d/$PROJECT_NAME.conf

	echo 'Created a virtual host'

	printf "Generating Apache configuration for mod_wsgi... " && \
		cd $PROJECT_ROOT && \
		source $ENV_NAME/bin/activate && \
		mod_wsgi-express module-config > /tmp/__apache_cfg__10-wsgi-config.conf && \
		deactivate && \
		sudo mv /tmp/__apache_cfg__10-wsgi-config.conf /etc/httpd/conf.modules.d/10-wsgi.conf && \
		sudo chmod +x /etc/httpd/conf.modules.d/10-wsgi.conf && \
		sudo restorecon -v /etc/httpd/conf.modules.d/10-wsgi.conf && \
		echo "OK"

	printf 'Telling SELinux to grant Apache access to Python and the project (this may take a while)... ' && \
		sudo chown -R apache:apache "$PROJECT_ROOT" && \
		set_fcontext httpd_sys_rw_content_t "${PROJECT_ROOT}(/.*)?" && \
		set_fcontext httpd_sys_script_exec_t "${PROJECT_ROOT}/${ENV_NAME}(/.*)?" && \
		set_fcontext httpd_sys_script_exec_t "${PROJECT_ROOT}/${PROJECT_NAME}/manage.py" && \
		set_fcontext httpd_sys_script_exec_t "${PROJECT_ROOT}/${PROJECT_NAME}/sh(/.*)?" && \
		set_fcontext httpd_sys_script_exec_t "${PROJECT_ROOT}/${PROJECT_NAME}/${PROJECT_NAME}(/.*)?" && \
		sudo restorecon -Rv "$PROJECT_ROOT" && \
		([[ ! -d $MICROMAMBA_ENV_DIR/$MICROMAMBA_ENV ]] || set_fcontext httpd_sys_script_exec_t "${MICROMAMBA_ENV_DIR}/${MICROMAMBA_ENV}(/.*)?") && \
		([[ ! -d $MICROMAMBA_ENV_DIR/$MICROMAMBA_ENV ]] || sudo restorecon -Rv "$MICROMAMBA_ENV_DIR/$MICROMAMBA_ENV") && \
		echo 'OK'

	printf "Reloading configuration... ";	\
		sudo systemctl restart httpd && \
		sudo touch $PROJECT_ROOT/$PROJECT_NAME/$PROJECT_NAME/wsgi.py && \
		echo "OK"
}


create_crons() {
	echo "Creating cron jobs..."
	sudo touch $CRON_PROCESSING_LOG
	sudo chown apache:apache $CRON_PROCESSING_LOG
	( sudo crontab -u apache -l 2>/dev/null | grep -v "$CRON_PROCESSING_TAG"; echo "$CRON_PROCESSING" ) | sudo crontab -u apache -

	sudo touch $CRON_CLEANUP_LOG
	sudo chown apache:apache $CRON_CLEANUP_LOG
	( sudo crontab -u apache -l 2>/dev/null | grep -v "$CRON_CLEANUP_TAG"; echo "$CRON_CLEANUP" ) | sudo crontab -u apache -
}


### Main ###
ENV_NAME="venv"
PROJECT_ROOT="/var/www/$PROJECT_NAME"

read_host_info
ensure_python
remove_old_installation
extract_tarball
create_venv
update_configuration
setup_apache
create_crons

echo Done.
