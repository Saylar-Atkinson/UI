const $uploadCsvForm = document.querySelector('#uploadcsv_form');
if ($uploadCsvForm !== null && $uploadCsvForm !== undefined) {
	$uploadCsvForm.addEventListener('submit', onSubmitCSVForm);
}


function onSubmitCSVForm(event) {
	if (event === null) {
		return;
	}

	const $form = event.target;
	const $fileInput = $form.querySelector('input[type=file]');
	const $previewSection = document.querySelector('#uploadcsv_preview_section');
	const $progressBar = $form.querySelector('progress');
	const $progressFileName = document.querySelector('#uploadcsv_progress_file_name');
	const $submitButton = $form.querySelector('button[type=submit]');

	if ($progressBar === null || $progressBar === undefined) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('Upload progress bar not found. Falling back to non-interactive upload.');
		return;
	}

	if (!submitCSVUploadForm($form, $progressBar)) {
		// also fall back to non-interactive upload if the AJAX submission fails for some reason.
		return;
	}

	setCSVUploadInProgress($progressBar, $progressFileName, $fileInput, $previewSection, $submitButton);
	lockForm($form);

	event.preventDefault();
}


function submitCSVUploadForm($form, $progressBar) {
	if ($form === null || $form === undefined || $progressBar === null || $progressBar === undefined) {
		return false;
	}

	const xhr = new window.XMLHttpRequest();
	xhr.onerror = (event) => onUploadError(xhr, event);
	xhr.ontimeout = (event) => onUploadError(xhr, event);
	xhr.upload.onprogress = (event) => { updateCSVUploadProgress($progressBar, event); };
	xhr.onload = () => onUploadSuccess(xhr);
	xhr.open($form.getAttribute('method'), $form.getAttribute('action'));
	xhr.setRequestHeader('Accept', 'application/json');
	xhr.send(new window.FormData($form));

	return true;
}


function setCSVUploadInProgress($progressBar, $progressFileName, $fileInput, $previewSection, $submitButton) {
	if ($previewSection !== null && $previewSection !== undefined) {
		$previewSection.classList.add('hidden');
	}
	if ($submitButton !== null && $submitButton !== undefined) {
		$submitButton.classList.add('hidden');
	}
	if ($progressBar !== null && $progressBar !== undefined) {
		$progressBar.parentNode.classList.remove('hidden');
	}
	if (
		$fileInput !== null &&
		$fileInput !== undefined &&
		$progressFileName !== null &&
		$progressFileName !== undefined
	) {
		const fileName = $fileInput.files.length > 0 ? $fileInput.files[0].name : '';
		$progressFileName.textContent = `"${fileName}"`;
	}
}


function updateCSVUploadProgress($progressBar, event) {
	if ($progressBar === null || $progressBar === undefined) {
		return;
	}

	if (event.lengthComputable) {
		$progressBar.setAttribute('max', event.total);
		$progressBar.setAttribute('value', event.loaded);
		$progressBar.textContent = `${Math.round((event.loaded / event.total) * 100)}%`;
	} else {
		$progressBar.removeAttribute('max');
		$progressBar.removeAttribute('value');
		$progressBar.textContent = '';
	}
}


function lockForm($form) {
	if ($form !== null && $form !== undefined) {
		$form
			.querySelectorAll('input, select, textarea, button')
			.forEach((element) => element.setAttribute('disabled', true));
	}
}

function onUploadError(xhr, event) {
	if (xhr === null || event === null) {
		return;
	}

	console.error('Upload failed due to a network error.');

	if (xhr.statusText) {
		console.error('StatusText:', xhr.statusText);
	}

	if (xhr.responseText) {
		console.error('Response Text:', xhr.responseText);
	}

	if (xhr.response) {
		console.error('Response:', xhr.response);
	}

	window.location.href = '{% url "upload_csv_failed" %}';
}


function onUploadSuccess(xhr) {
	if (xhr === null) {
		return;
	}

	let response = null;

	try {
		response = JSON.parse(xhr.response);
	} catch (error) {
		console.error('Failed to parse JSON response:', error);
		window.location.href = '{% url "upload_csv_failed" %}';
		return;
	}

	if (response && typeof response === 'object' && response.job_id) {
		window.location.href = '{% url "job_status" job_id=0 %}'.replace('0', response.job_id);
		return;
	}

	const invalidFile = typeof response.invalid_file === 'string' ? response.invalid_file : '';
	const invalidForm = typeof response.invalid_input === 'boolean' ? response.invalid_input : false;

	if (invalidForm) {
		window.location.href = '{% url "upload_form_invalid" %}';
	} else if (invalidFile.length > 0) {
		window.location.href = '{% url "save_csv_failed" filename=0 %}'.replace('0', encodeURIComponent(invalidFile));
	} else {
		window.location.href = '{% url "upload_csv_failed" %}';
	}
}
