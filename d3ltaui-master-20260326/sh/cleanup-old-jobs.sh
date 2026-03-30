#!/bin/bash

if ! [[ -d venv && -d d3ltaui ]]
then
	echo "Please run this script from the root project directory."
	exit 1
fi


run_script() {
	LOCKFILE="/tmp/cleanup_old_d3lta_jobs.lock"

	if flock -n "$LOCKFILE" python3.11 manage.py cleanup_old_jobs; then
		return 0
	else
		return 1
	fi
}


source venv/bin/activate && cd d3ltaui && run_script
