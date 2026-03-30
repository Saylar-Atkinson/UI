function onClusterChange($select) {
	if ($select === null || $select.options === null || $select.options === undefined) {
		return;
	}

	const $previewContainer = document.querySelector('#cluster_preview_container');
	if ($previewContainer === null || $previewContainer === undefined) {
		// eslint-disable-next-line no-console, no-undef
		console.error('Could not display cluster preview. Preview container not found.');
		return;
	}


	$select.disabled = true;

	const $currentTable = $previewContainer.querySelector('table');
	if ($currentTable) {
		$currentTable.style.opacity = 0.5;
	}

	const $currentDownloadButton = $previewContainer.querySelector('a');
	if ($currentDownloadButton) {
		$currentDownloadButton.href = '';
		$currentDownloadButton.style.opacity = 0.5;
		$currentDownloadButton.style.pointerEvents = 'none';
	}

	const previewUrl = $select.value;
	if (previewUrl === null || previewUrl === undefined || previewUrl.trim() === '') {
		$previewContainer.textContent = 'No cluster selected.';
		$select.disabled = false;
		return;
	}

	window.fetch(previewUrl)
		.then(response => onClusterPreviewLoad($select, $previewContainer, response))
		.catch(error => onClusterPreviewError($select, $previewContainer, error));
}

onClusterChange(document.querySelector('#select_job_output_cluster'));


function onClusterPreviewLoad($select, $previewContainer, response) {
	if (!response.ok) {
		onClusterPreviewError($select, $previewContainer, `Server responded with status ${response.status}`);
		return;
	}

	response.text()
		.then(previewHtml => {
			$previewContainer.innerHTML = previewHtml;
			$select.disabled = false;
		})
		.catch(error => onClusterPreviewError($select, $previewContainer, error));
}


function onClusterPreviewError($select, $previewContainer, error) {
	// eslint-disable-next-line no-console, no-undef
	console.error(`Failed to load cluster preview. ${error}`);
	$previewContainer.textContent = 'Failed to load cluster preview.';
	$select.disabled = false;
}
