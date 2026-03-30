#!/bin/bash

if ! [[ -d venv && -d d3ltaui ]]
then
	echo "Please run this script from the root project directory."
	exit 1
fi

delete_d3lta_garbage() {
	rm -rf use_model_kaggle
	rm -f *.ftz
	rm -f *.pkl
}

run_script() {
	LOCKFILE="/tmp/process_jobs_with_d3lta.lock"

	if flock -n "$LOCKFILE" python3.11 manage.py process_jobs; then
		return 0
	else
		return 1
	fi
}

source venv/bin/activate \
	&& cd d3ltaui \
	&& run_script \
	&& delete_d3lta_garbage
