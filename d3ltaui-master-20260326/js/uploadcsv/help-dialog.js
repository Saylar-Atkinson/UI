function openHelpDialog(title, body) {
	const $dialog = document.querySelector('dialog');
	if (!$dialog) {
		// eslint-disable-next-line no-console, no-undef
		console.error('Cannot display help popup. <dialog> element not found.');
		return;
	}

	const $title = $dialog.querySelector('article header h3');
	const $body = $dialog.querySelector('article p');

	if (!$title || !$body) {
		// eslint-disable-next-line no-console, no-undef
		console.error('Cannot display help popup. Missing title or body containers.');
		return;
	}

	$title.textContent = title;
	$body.textContent = body;

	$dialog.showModal();
}


function closeHelpDialog() {
	const $dialog = document.querySelector('dialog');
	if ($dialog === null || $dialog === undefined) {
		// eslint-disable-next-line no-console, no-undef
		console.error('Cannot close help popup. <dialog> element not found.');
		return;
	}

	$dialog.close();
}
