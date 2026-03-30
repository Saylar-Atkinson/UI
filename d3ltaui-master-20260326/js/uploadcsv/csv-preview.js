const MAX_PREVIEW_CELL_TEXT_LENGTH = 3000;

function nRowsLeft(n) {
	return `... ${n} more`;
}


async function onCSV($input) {
	if ($input === undefined || $input === null) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('File input is NULL');
		return;
	}

	if (!($input.files instanceof window.FileList) || $input.files.length === 0) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('The "files" property is not an instance of FileList or is an empty list.');
		return;
	}

	const isPreviewLoading = showUpdatePreviewLoading(
		document.querySelector('#uploadcsv_preview_section'),
		document.querySelector('#uploadcsv_preview_loading_label')
	);

	if (!isPreviewLoading) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('Could not show the update preview section HTML element.');
		return;
	}

	const startTime = window.performance.now();
	const { fileName,
		header,
		lineCount,
		rows,
		separator
	} = await parseCSV($input.files[0]);

	// eslint-disable-next-line
	console.log(`"${fileName}" parsed in: ${performance.now() - startTime} ms.`);

	const previewSuccessful = updatePreviewTable(
		document.querySelector('#uploadcsv_preview_loading_label'),
		document.querySelector('#uploadcsv_preview_failed_label'),
		document.querySelector('#uploadcsv_preview_table'),
		header,
		rows,
		lineCount - 1
	);

	updatePreviewLineCount(
		document.querySelector('#uploadcsv_preview_line_count_label'),
		document.querySelector('#uploadcsv_preview_line_count'),
		previewSuccessful ? lineCount : -1
	);

	updateDocumentDropdowns(
		document.querySelector('#uploadcsv_preview_file_options_container'),
		document.querySelector('#uploadcsv_preview_doc_content'),
		previewSuccessful ? header : []
	);

	updateSeparatorDropdown(
		document.querySelector('#uploadcsv_preview_csv_column_separator'),
		separator
	);
}


function showUpdatePreviewLoading($section, $label) {
	if ($section === null || $section === undefined) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('Could not find the preview section.');
		return false;
	}

	if ($label === null || $label === undefined) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('Could not find the preview loading label.');
		return false;
	}

	$section.classList.remove('hidden');
	$label.classList.remove('hidden');
	return true;
}


function updatePreviewLineCount($container, $label, lineCount) {
	if ($container === null || $container === undefined || $label === null || $label === undefined) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('Could not find line count elements.');
		return;
	}

	if (lineCount < 0) {
		$container.classList.add('hidden');
		return;
	}

	$container.classList.remove('hidden');
	$label.textContent = lineCount;
}


function updatePreviewTable($previewLoading, $previewFailed, $table, header, rows, rowCount) {
	if ($table === null || $table === undefined) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('Could not find preview table.');
		return false;
	}

	$table.classList.remove('hidden');
	if ($previewLoading !== null && $previewLoading !== undefined) {
		$previewLoading.classList.add('hidden');
	}
	if ($previewFailed !== null && $previewFailed !== undefined) {
		$previewFailed.classList.add('hidden');
	}

	if (!setThead($table, header) || !setTbody($table, rows, rowCount)) {
		showPreviewFailed($previewFailed, $table);
		return false;
	}

	return true;
}


function setThead($table, header) {
	if (!Array.isArray(header) || header.length === 0) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('The preview header must be a non-empty array.');
		return false;
	}

	const $thead = $table !== null ? $table.querySelector('thead') : null;
	if ($thead === null) {
		return false;
	}

	$thead.textContent = '';

	const $tr = document.createElement('tr');
	for (const col of header) {
		const $td = document.createElement('th');
		$td.textContent = col;
		$tr.appendChild($td);
	}

	if ($tr.childElementCount === 0) {
		return false;
	}

	$thead.appendChild($tr);

	return true;
}


function setTbody($table, rows, rowCount) {
	if (!Array.isArray(rows)) {
		// eslint-disable-next-line no-console, no-undef
		console.warn(
			'Incorrectly formatted preview rows. Expected an array containing rows, where each row is a String array.'
		);
		return false;
	}

	const $tbody = $table !== null ? $table.querySelector('tbody') : null;
	if ($tbody === null) {
		return false;
	}

	$tbody.textContent = '';

	for (const row of rows) {
		if (row === null) {
			continue;
		}

		const $tr = document.createElement('tr');
		for (const cell of row) {
			const $cellContent = document.createElement('div');

			// just in case...
			const truncated = typeof cell === 'string' && cell.length > MAX_PREVIEW_CELL_TEXT_LENGTH ? `${cell.substring(0, MAX_PREVIEW_CELL_TEXT_LENGTH)}...` : cell;
			$cellContent.textContent = truncated;
			$cellContent.setAttribute('title', truncated);

			const $td = document.createElement('td');
			$td.appendChild($cellContent);
			$tr.appendChild($td);
		}

		if ($tr.childElementCount > 0) {
			$tbody.appendChild($tr);
		}
	}

	if (rowCount > rows.length && rows.length > 0) {
		const $td = document.createElement('td');
		$td.setAttribute('colspan', rows[0].length);
		$td.textContent = nRowsLeft(rowCount - rows.length);

		const $tr = document.createElement('tr');
		$tr.appendChild($td);

		$tbody.appendChild($tr);
	}

	return $tbody.childElementCount > 0;
}


function showPreviewFailed($previewFailed, $table) {
	if ($table !== null && $table !== undefined) {
		$table.classList.add('hidden');
	}

	if ($previewFailed !== null && $previewFailed !== undefined) {
		$previewFailed.classList.remove('hidden');
	}
}


function updateDocumentDropdowns($container, $docText, header) {
	if ($container === null) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('Could not find the column picker container element.');
		return;
	}

	$container.classList.remove('hidden');

	if ($docText !== null) {
		$docText.textContent = '';
		// we can't reuse the same options in a different <select>, so we generate a new Array
		headerToOptions(header).forEach(o => $docText.appendChild(o));
	}
}


function headerToOptions(header) {
	const blankOption = document.createElement('option');
	blankOption.textContent = '--';
	blankOption.setAttribute('value', '');
	blankOption.setAttribute('selected', true);

	const safeHeader = Array.isArray(header) ? header : [];

	return [
		blankOption,
		...safeHeader.map(column => {
			const option = document.createElement('option');
			option.setAttribute('value', column);
			option.textContent = column;
			return option;
		})
	];
}


function updateSeparatorDropdown($select, separator) {
	if ($select === null || $select === undefined) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('Could not find the separator select element.');
		return;
	}

	if (typeof separator !== 'string' || separator.length === 0) {
		return;
	}

	$select.value = separator === '\t' ? '\\t' : separator;
}
