let jobCopyCheckMarkClearTimeout = null;

function copyJobIdToClipboard() {
	const $idContainer = document.getElementById('job_id');
	if ($idContainer === null || $idContainer === undefined) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('Could not find element with id "job_id". Cannot copy job id to clipboard.');
		return;
	}

	const textToCopy = ($idContainer.textContent || '').trim();

	if (noClipboardSupport()) {
		showJobIdNotCopied('Clipboard API is not available in this context.');
		return;
	}

	try {
		window.navigator.clipboard.writeText(textToCopy)
			.then(showJobIdCopied)
			.catch(showJobIdNotCopied);
	} catch (error) {
		showJobIdNotCopied(error);
	}
}


function noClipboardSupport() {
	return !window.navigator ||
		!window.navigator.clipboard ||
		typeof window.navigator.clipboard.writeText !== 'function';
}


function showJobIdCopied() {
	const $icon = document.getElementById('copy_job_id_status');

	if ($icon !== null && $icon !== undefined) {
		$icon.textContent = '✓';
		hideDelayedJobCopiedIcon($icon);
	}
}


function showJobIdNotCopied(error) {
	// eslint-disable-next-line no-console, no-undef
	console.error(`Failed to copy job id to clipboard. ${error}`);

	const $icon = document.getElementById('copy_job_id_status');

	if ($icon !== null && $icon !== undefined) {
		$icon.textContent = ' (failed)';
		hideDelayedJobCopiedIcon($icon);
	}
}


function hideDelayedJobCopiedIcon($icon) {
	if ($icon !== null && $icon !== undefined) {
		window.clearTimeout(jobCopyCheckMarkClearTimeout);
		jobCopyCheckMarkClearTimeout = window.setTimeout(() => { $icon.textContent = ''; }, 2000);
	}
}
