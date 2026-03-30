#!/usr/bin/env bash

ENV_NAME="py311"
MICROMAMBA_BIN="$HOME/.local/bin/micromamba"
MICROMAMBA_ENV_DIR="/var/micromamba/envs/"


PYTHON_INSTALLED=0


error() {
	echo "[ERROR] $1"
}


check_system_python() {
	echo "Checking for system Python 3.11..."
	if command -v python3.11 >/dev/null 2>&1; then
		echo "System Python 3.11 already installed."
		PYTHON_INSTALLED=1
	else
		echo "System Python 3.11 not found."
	fi
}


check_micromamba_env() {
	if [ "$PYTHON_INSTALLED" -eq 1 ]; then
		return
	fi

	if command -v micromamba >/dev/null 2>&1; then
		echo "Checking micromamba environment '${ENV_NAME}'..."
		if micromamba env list | awk '{print $1}' | grep -q "${ENV_NAME}"; then
			echo "Micromamba environment '${ENV_NAME}' already exists."
			PYTHON_INSTALLED=1
		fi
	fi
}


check_dnf_for_python() {
	if [ "$PYTHON_INSTALLED" -eq 1 ]; then
		return
	fi

	echo "Checking DNF repositories for python3.11..."

	if dnf search -q python3.11 | grep -q python3.11; then
		echo "python3.11 available via dnf."
		sudo dnf install -y python3.11 python3.11-pip
		PYTHON_INSTALLED=1
	else
		echo "python3.11 not available via dnf."
	fi
}


install_micromamba() {
	if command -v micromamba >/dev/null 2>&1; then
		echo "micromamba already installed."
		return
	fi

	echo "Installing micromamba..."
	curl -Ls https://micro.mamba.pm/install.sh | bash

	if [ -x "$MICROMAMBA_BIN" ]; then
		export PATH="$HOME/.local/bin:$PATH"
		echo "micromamba installed successfully."
	else
		error "micromamba installation failed."
	fi
}


create_micromamba_env() {
	if [ "$PYTHON_INSTALLED" -eq 1 ]; then
		return
	fi

	echo "Creating micromamba environment '${ENV_NAME}' with Python 3.11..."

	if ! command -v micromamba >/dev/null 2>&1; then
		error "micromamba not available. Cannot create environment."
		return
	fi

	eval "$(micromamba shell hook --shell=bash)" && \
		sudo mkdir -p "$MICROMAMBA_ENV_DIR" && \
		sudo chmod +xr "$MICROMAMBA_ENV_DIR" && \
		sudo chown `whoami` "$MICROMAMBA_ENV_DIR" && \
		micromamba create -y --prefix "${MICROMAMBA_ENV_DIR}/${ENV_NAME}" python=3.11 && \
		PYTHON_INSTALLED=1 && \
		echo "Environment '${ENV_NAME}' created."
}


### Main ###
check_system_python
check_dnf_for_python

if [ "$PYTHON_INSTALLED" -eq 0 ]; then
	check_micromamba_env
	install_micromamba
	create_micromamba_env
fi

if [ "$PYTHON_INSTALLED" -eq 1 ]; then
	echo "Python 3.11 setup ensured."
else
	error "Python 3.11 could not be ensured."
	exit 1
fi

sudo dnf -y install policycoreutils-python-utils httpd httpd-tools httpd-devel tar gcc gcc-c++
echo "Enabling Apache2..."
sudo systemctl enable httpd
sudo systemctl start httpd

echo "Adding Apache2 to firewalld..."
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
