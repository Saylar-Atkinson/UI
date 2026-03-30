function autoReloadOnStatusChange(current, statusUrl, retryInterval) {
	if (retryInterval <= 0 || (current !== 'PENDING' && current !== 'PROCESSING')) {
		return;
	}

	window.fetch(statusUrl)
		.then(response => {
			if (!response.ok) {
				// eslint-disable-next-line no-console, no-undef
				console.warn('Auto-reload on status change disabled. Server returned a non-OK response.');
				return;
			}

			response.text()
				.then(text => {
					if (text !== current) {
						window.location.reload();
					} else {
						window.setTimeout(
							() => autoReloadOnStatusChange(current, statusUrl, retryInterval),
							retryInterval
						);
					}
				})
				// eslint-disable-next-line no-console, no-undef
				.catch(error => console.warn(`Auto-reload on status change disabled. ${error}`));
		})
		// eslint-disable-next-line no-console, no-undef
		.catch(error => console.warn(`Auto-reload on status change disabled. ${error}`));
}
