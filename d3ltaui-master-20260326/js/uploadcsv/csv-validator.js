async function parseCSV(file) {
	if (!(file instanceof window.File)) {
		// eslint-disable-next-line no-console, no-undef
		console.warn('The first element in "files" is not an instance of File.');
		return {
			fileName: '',
			header: [],
			lineCount: 0,
			rows: [],
			separator: ''
		};
	}

	const reader = file.stream().getReader();
	const decoder = new window.TextDecoder();

	let { value, done } = await reader.read();

	let buffer = '';
	let lineCount = 0;
	const previewLines = [];

	while (!done) {
		buffer += decoder.decode(value, { stream: true });

		const lines = buffer.split('\n');
		buffer = lines.pop(); // keep last partial line

		for (const line of lines) {
			lineCount++;
			if (previewLines.length < 10) {
				previewLines.push(line);
			}
		}

		({ value, done } = await reader.read());
	}

	// flush any remaining part of a multi-byte character
	buffer += decoder.decode();

	if (buffer) {
		lineCount++;
		if (previewLines.length < 10) {
			previewLines.push(buffer);
		}
	}

	let fileName = typeof file.name === 'string' && file.name.length > 0 ? file.name : null;

	if (fileName === null && typeof file.fileName === 'string' && file.fileName.length > 0) {
		fileName = file.fileName;
	}

	if (fileName === null) {
		fileName = 'file';
	}

	const { header, rows, separator } = previewLinesToArrays(previewLines);

	return {
		fileName,
		header,
		lineCount,
		rows,
		separator
	};
}


// --- Separator Detection ---
function detectSeparator(lines) {
	const separators = [',', ';', '\t', '|'];
	const firstLine = lines.find(l => l.trim().length > 0) || '';

	let bestSep = ',';
	let maxCols = 0;

	for (const sep of separators) {
		const cols = parseCsvLine(firstLine, sep);
		if (cols.length > maxCols) {
			maxCols = cols.length;
			bestSep = sep;
		}
	}

	return bestSep;
}


// --- Core CSV Parser (handles multiline quoted fields) ---
function parseCsv(text, separator) {
	const rows = [];
	let currentRow = [];
	let currentValue = '';
	let inQuotes = false;

	for (let i = 0; i < text.length; i++) {
		const char = text[i];
		const nextChar = text[i + 1];

		if (char === '"') {
			if (inQuotes && nextChar === '"') {
				currentValue += '"';
				i++;
			} else {
				inQuotes = !inQuotes;
			}
		} else if (char === separator && !inQuotes) {
			currentRow.push(currentValue.trim());
			currentValue = '';
		} else if ((char === '\n' || char === '\r') && !inQuotes) {
			if (char === '\r' && nextChar === '\n') i++; // handle CRLF

			currentRow.push(currentValue.trim());
			rows.push(currentRow);

			currentRow = [];
			currentValue = '';
		} else {
			currentValue += char;
		}
	}

	// Push last value if any
	if (currentValue.length > 0 || currentRow.length > 0) {
		currentRow.push(currentValue.trim());
		rows.push(currentRow);
	}

	return rows;
}


// --- Simple line parser (for separator detection only) ---
function parseCsvLine(line, separator) {
	const result = [];
	let current = '';
	let inQuotes = false;

	for (let i = 0; i < line.length; i++) {
		const char = line[i];
		const nextChar = line[i + 1];

		if (char === '"') {
			if (inQuotes && nextChar === '"') {
				current += '"';
				i++;
			} else {
				inQuotes = !inQuotes;
			}
		} else if (char === separator && !inQuotes) {
			result.push(current);
			current = '';
		} else {
			current += char;
		}
	}

	result.push(current);
	return result;
}


function previewLinesToArrays(previewLines) {
	if (!previewLines || previewLines.length === 0) {
		return { header: [], rows: [], separator: '' };
	}

	const text = previewLines.join('\n');
	const separator = detectSeparator(previewLines);
	const csvRows = parseCsv(text, separator);

	if (csvRows.length === 0) {
		return { header: [], rows: [] };
	}

	const [header, ...rows] = csvRows;

	return { header, rows, separator };
}
