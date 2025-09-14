const git_message = 'Trying to obtain list from GIT repo';
const wait_message = 'Please wait..';
const error_message = 'Failed, please try again';

// Global variable to store the original occupied list data
let originalOccupiedData = null;

async function get_cidr() {
	const subnet_size = document.getElementById('subnet')?.value || '';
	const requiredrange = document.getElementById('range')?.value || '';
	const reason = document.getElementById('reason')?.value || '';

	// Frontend validation
	const validationError = validateGetCidrInput(reason);
	if (validationError) {
		const containerElement = document.getElementById('cidr-result-container');
		const titleElement = document.getElementById('cidr-result-title');
		const messagesElement = document.getElementById('cidr_messages');
		const outputElement = document.getElementById('cidr_output');
		
		// Show the result container with error context
		containerElement.style.display = 'block';
		titleElement.innerHTML = "Validation Error:";
		titleElement.className = "error-title";
		
		// Hide the messages element to avoid empty line
		messagesElement.style.display = "none";
		messagesElement.innerHTML = "";
		messagesElement.className = "";
		
		outputElement.innerHTML = validationError;
		outputElement.className = "validation-error";
		
		// Hide copy button during validation errors
		document.getElementById('copy-cidr-btn').style.display = 'none';
		return;
	}
	
	// Show the result container with success context and clear any previous validation error styling
	const containerElement = document.getElementById('cidr-result-container');
	const titleElement = document.getElementById('cidr-result-title');
	const messagesElement = document.getElementById('cidr_messages');
	containerElement.style.display = 'block';
	titleElement.innerHTML = "The received CIDR is";
	titleElement.className = "";
	messagesElement.style.display = "block";
	messagesElement.className = "";
	document.getElementById('cidr_output').className = "";

	const url = `/get-cidr?subnet_size=${subnet_size}&requiredrange=${requiredrange}&reason=${reason}`;

	try {
		document.getElementById('cidr_messages').innerHTML = "Retrieving unique cidr..";
		document.getElementById('cidr_output').innerHTML = wait_message;
		document.getElementById('copy-cidr-btn').style.display = 'none';
		
		const response = await fetch(url);
		const cidrRes = await response.text();
		document.getElementById('cidr_output').innerHTML = (cidrRes);
		document.getElementById('cidr_messages').innerHTML = "Done!";
		
		// Show copy button if we have a valid CIDR response
		if (cidrRes && !cidrRes.includes('error') && !cidrRes.includes('Error')) {
			document.getElementById('copy-cidr-btn').style.display = 'block';
		}

	}
	catch (e) {
		document.getElementById('cidr_messages').innerHTML = `Server error: ${e.message}`;
		document.getElementById('cidr_output').innerHTML = error_message;
		document.getElementById('copy-cidr-btn').style.display = 'none';
	}
}

async function get_occupied_list() {
	const url = '/get-occupied-list';
	
	// Show the result container
	const containerElement = document.getElementById('occupied-result-container');
	containerElement.style.display = 'block';
	
	try {
	  document.getElementById('occupied_messages').innerHTML = git_message;
	  document.getElementById('occupied_output').innerHTML = wait_message;
	  const response = await fetch(url);
	  const occupiedlist = await response.text();
	  
	  // Store the original data for filtering
	  originalOccupiedData = JSON.parse(occupiedlist);
	  
	  // Display the formatted data
	  displayOccupiedList(originalOccupiedData);
	  
	  document.getElementById('occupied_messages').innerHTML = "Done!";
	  
	  // Show the search container
	  document.getElementById('search-container').style.display = 'block';
	  
	  // Clear any previous search
	  document.getElementById('cidr-search').value = '';
	  
	} catch (e) {
	  document.getElementById('occupied_messages').innerHTML = `Server error: ${e.message}`;
	  document.getElementById('occupied_output').innerHTML = error_message;
	  // Hide search container on error
	  document.getElementById('search-container').style.display = 'none';
	}
}

async function get_next_cidr() {
	const subnet_size = document.getElementById('subnet')?.value || '';
	const requiredrange = document.getElementById('range')?.value || '';
	const reason = document.getElementById('reason')?.value || '';

	// Frontend validation
	const validationError = validateGetCidrInput(reason);
	if (validationError) {
		const containerElement = document.getElementById('cidr-result-container');
		const titleElement = document.getElementById('cidr-result-title');
		const messagesElement = document.getElementById('cidr_messages');
		const outputElement = document.getElementById('cidr_output');
		
		// Show the result container with error context
		containerElement.style.display = 'block';
		titleElement.innerHTML = "Validation Error:";
		titleElement.className = "error-title";
		
		// Hide the messages element to avoid empty line
		messagesElement.style.display = "none";
		messagesElement.innerHTML = "";
		messagesElement.className = "";
		
		outputElement.innerHTML = validationError;
		outputElement.className = "validation-error";
		
		// Hide copy button during validation errors
		document.getElementById('copy-cidr-btn').style.display = 'none';
		return;
	}
	
	// Show the result container with success context and clear any previous validation error styling
	const containerElement = document.getElementById('cidr-result-container');
	const titleElement = document.getElementById('cidr-result-title');
	const messagesElement = document.getElementById('cidr_messages');
	containerElement.style.display = 'block';
	titleElement.innerHTML = "The received CIDR is";
	titleElement.className = "";
	messagesElement.style.display = "block";
	messagesElement.className = "";
	document.getElementById('cidr_output').className = "";

	const url = `/get-next-cidr-no-push?subnet_size=${subnet_size}&requiredrange=${requiredrange}&reason=${reason}`;
	try {
		document.getElementById('cidr_messages').innerHTML = git_message;
		document.getElementById('cidr_output').innerHTML = wait_message;
		document.getElementById('copy-cidr-btn').style.display = 'none';
		
		const response = await fetch(url);
		const occupiedlist = await response.text();
		document.getElementById('cidr_output').innerHTML = occupiedlist;
		document.getElementById('cidr_messages').innerHTML = "Done!";
		
		// Show copy button if we have a valid CIDR response
		if (occupiedlist && !occupiedlist.includes('error') && !occupiedlist.includes('Error')) {
			document.getElementById('copy-cidr-btn').style.display = 'block';
		}
	}
	catch (e) {
		document.getElementById('cidr_messages').innerHTML = `Server error: ${e.message}`;
		document.getElementById('cidr_output').innerHTML = error_message;
		document.getElementById('copy-cidr-btn').style.display = 'none';

	}
}

async function delete_cidr_from_list() {
	const cidr_deletion = document.getElementById('cidr_deletion')?.value || '';

	// Frontend validation for CIDR
	const cidrValidationError = validateCIDRInput(cidr_deletion);
	if (cidrValidationError) {
		const containerElement = document.getElementById('delete-result-container');
		const titleElement = document.getElementById('delete-result-title');
		
		containerElement.style.display = 'block';
		titleElement.innerHTML = "Validation Error:";
		titleElement.className = "error-title";
		
		document.getElementById('delete_messages').innerHTML = cidrValidationError;
		document.getElementById('delete_messages').className = "validation-error";
		return;
	}
	
	// Show the result container and clear any previous validation error styling
	const containerElement = document.getElementById('delete-result-container');
	const titleElement = document.getElementById('delete-result-title');
	containerElement.style.display = 'block';
	titleElement.innerHTML = "Result:";
	titleElement.className = "";
	document.getElementById('delete_messages').className = "";

	const url = `/delete-cidr-from-list?cidr_deletion=${cidr_deletion}`;
	try {
		document.getElementById('delete_messages').innerHTML = git_message;
		const response = await fetch(url);
		const occupiedlist = await response.text();
		document.getElementById('delete_messages').innerHTML = occupiedlist;
	}
	catch (e) {
		document.getElementById('delete_messages').innerHTML = `Server error: ${e.message}`;
	}
}

async function add_cidr_manually() {
	const cidr = document.getElementById('cidr')?.value || '';
	const reason = document.getElementById('add-reason')?.value || '';

	// Frontend validation for reason
	const reasonValidationError = validateGetCidrInput(reason);
	if (reasonValidationError) {
		const containerElement = document.getElementById('add-result-container');
		const titleElement = document.getElementById('add-result-title');
		
		containerElement.style.display = 'block';
		titleElement.innerHTML = "Validation Error:";
		titleElement.className = "error-title";
		
		document.getElementById('add_messages').innerHTML = reasonValidationError;
		document.getElementById('add_messages').className = "validation-error";
		return;
	}
	
	// Frontend validation for CIDR
	const cidrValidationError = validateCIDRInput(cidr);
	if (cidrValidationError) {
		const containerElement = document.getElementById('add-result-container');
		const titleElement = document.getElementById('add-result-title');
		
		containerElement.style.display = 'block';
		titleElement.innerHTML = "Validation Error:";
		titleElement.className = "error-title";
		
		document.getElementById('add_messages').innerHTML = cidrValidationError;
		document.getElementById('add_messages').className = "validation-error";
		return;
	}
	
	// Show the result container and clear any previous validation error styling
	const containerElement = document.getElementById('add-result-container');
	const titleElement = document.getElementById('add-result-title');
	containerElement.style.display = 'block';
	titleElement.innerHTML = "Result:";
	titleElement.className = "";
	document.getElementById('add_messages').className = "";

	const url = `/add-cidr-manually?cidr=${cidr}&reason=${reason}`;

	try {
		document.getElementById('add_messages').innerHTML = "Checking if the CIDR is valid and NOT occupied";

		const response = await fetch(url);

		const adding_response = await response.text();
		document.getElementById('add_messages').innerHTML = adding_response;

	}
	catch (e) {
		document.getElementById('add_messages').innerHTML = `Server error: ${e.message}`;
	}
}

// Function to display the occupied CIDR list in a formatted way
function displayOccupiedList(data) {
	const outputElement = document.getElementById('occupied_output');
	
	if (Object.keys(data).length === 0) {
		outputElement.innerHTML = `<div class="cidr-table-container"><div class="empty-state"><i class="fas fa-info-circle" style="font-size: 24px; margin-bottom: 10px; display: block;"></i>No occupied CIDR blocks found.</div></div>`;
		return;
	}

	// Create a structured HTML table for better presentation
	const totalCount = Object.keys(data).length;
	let tableHTML = `<div class="cidr-table-container"><div class="cidr-table-header"><div class="cidr-header-item">Reason</div><div class="cidr-header-item">CIDR Block</div><div class="cidr-header-item">Created</div></div><div class="cidr-table-body">`;

	// Sort entries by timestamp (newest first)
	const sortedEntries = Object.entries(data).sort((a, b) => {
		const timestampA = parseInt(a[0].match(/-(\d+)$/)?.[1] || '0');
		const timestampB = parseInt(b[0].match(/-(\d+)$/)?.[1] || '0');
		return timestampB - timestampA;
	});

	for (const [key, cidr] of sortedEntries) {
		// Extract timestamp for date display, but keep original key as reason
		const match = key.match(/^(.+)-(\d+)$/);
		const timestamp = match ? parseInt(match[2]) : 0;
		
		let formattedDate = 'Unknown';
		if (timestamp) {
			const dateObj = new Date(timestamp * 1000);
			const hours = dateObj.getHours().toString().padStart(2, '0');
			const minutes = dateObj.getMinutes().toString().padStart(2, '0');
			const day = dateObj.getDate().toString().padStart(2, '0');
			const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
			const year = dateObj.getFullYear().toString().slice(-2);
			formattedDate = `${hours}:${minutes} ${day}/${month}/${year}`;
		}
		
		tableHTML += `<div class="cidr-table-row"><div class="cidr-cell reason-cell">${key}</div><div class="cidr-cell cidr-cell-value">${cidr}</div><div class="cidr-cell date-cell">${formattedDate}</div></div>`;
	}

	tableHTML += `</div><div class="cidr-table-footer"><div class="cidr-count-info"><i class="fas fa-list"></i> Total: ${totalCount} CIDR block${totalCount !== 1 ? 's' : ''}</div></div></div>`;

	outputElement.innerHTML = tableHTML;
}

// Function to filter the CIDR list based on search input
function filterCIDRList() {
	if (!originalOccupiedData) {
		return; // No data to filter
	}
	
	const searchTerm = document.getElementById('cidr-search').value.toLowerCase().trim();
	
	if (searchTerm === '') {
		// Show all data if search is empty
		displayOccupiedList(originalOccupiedData);
		document.getElementById('occupied_messages').innerHTML = "Done!";
		return;
	}
	
	// Filter the data based on search term
	const filteredData = {};
	let matchCount = 0;
	
	for (const [key, cidr] of Object.entries(originalOccupiedData)) {
		const reason = key.replace(/-\d+$/, '').toLowerCase();
		const cidrLower = cidr.toLowerCase();
		
		// Check if search term matches reason or CIDR
		if (reason.includes(searchTerm) || cidrLower.includes(searchTerm)) {
			filteredData[key] = cidr;
			matchCount++;
		}
	}
	
	// Display filtered results
	displayOccupiedList(filteredData);
	
	// Update message with filter results
	document.getElementById('occupied_messages').innerHTML = `Filtered results`;
}

// Frontend validation function for Get CIDR operations
function validateGetCidrInput(reason) {
	// Check if reason is empty or only whitespace
	if (!reason || reason.trim() === '') {
		return "You must specify a reason, this field is mandatory!";
	}
	
	// Check if reason contains whitespaces (as mentioned in the UI)
	if (reason.includes(' ')) {
		return "Reason should not contain whitespaces. Please use underscores or hyphens instead.";
	}
	
	// Check minimum length
	if (reason.trim().length < 3) {
		return "Reason must be at least 3 characters long.";
	}
	
	// Check for valid characters (alphanumeric, hyphens, underscores)
	const validReasonPattern = /^[a-zA-Z0-9_-]+$/;
	if (!validReasonPattern.test(reason)) {
		return "Reason can only contain letters, numbers, hyphens, and underscores.";
	}
	
	return null; // No validation errors
}

// Frontend validation function for CIDR input
function validateCIDRInput(cidr) {
	// Check if CIDR is empty
	if (!cidr || cidr.trim() === '') {
		return "CIDR field is mandatory!";
	}
	
	// Basic CIDR format validation (IP/prefix)
	const cidrPattern = /^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/;
	if (!cidrPattern.test(cidr.trim())) {
		return "Invalid CIDR format. Expected format: 192.168.1.0/24";
	}
	
	// Validate IP address parts and prefix
	const [ip, prefix] = cidr.trim().split('/');
	const ipParts = ip.split('.');
	
	// Check each IP octet
	for (let i = 0; i < ipParts.length; i++) {
		const octet = parseInt(ipParts[i]);
		if (isNaN(octet) || octet < 0 || octet > 255) {
			return `Invalid IP address: octet ${i + 1} must be between 0-255`;
		}
	}
	
	// Check prefix length
	const prefixNum = parseInt(prefix);
	if (isNaN(prefixNum) || prefixNum < 0 || prefixNum > 32) {
		return "Invalid prefix length: must be between 0-32";
	}
	
	return null; // No validation errors
}

// Function to copy CIDR to clipboard
async function copyCIDRToClipboard() {
	const cidrOutput = document.getElementById('cidr_output');
	const copyButton = document.getElementById('copy-cidr-btn');
	
	if (!cidrOutput || !cidrOutput.textContent.trim()) {
		return;
	}
	
	try {
		// Get the CIDR text and clean it up
		const cidrText = cidrOutput.textContent.trim();
		
		// Copy to clipboard
		await navigator.clipboard.writeText(cidrText);
		
		// Show success feedback
		copyButton.classList.add('copied');
		copyButton.innerHTML = '<i class="fas fa-check"></i>';
		
		// Reset button after 2 seconds
		setTimeout(() => {
			copyButton.classList.remove('copied');
			copyButton.innerHTML = '<i class="fas fa-copy"></i>';
		}, 2000);
		
	} catch (err) {
		// Fallback for older browsers
		try {
			const textArea = document.createElement('textarea');
			textArea.value = cidrOutput.textContent.trim();
			document.body.appendChild(textArea);
			textArea.select();
			document.execCommand('copy');
			document.body.removeChild(textArea);
			
			// Show success feedback
			copyButton.classList.add('copied');
			copyButton.innerHTML = '<i class="fas fa-check"></i>';
			
			// Reset button after 2 seconds
			setTimeout(() => {
				copyButton.classList.remove('copied');
				copyButton.innerHTML = '<i class="fas fa-copy"></i>';
			}, 2000);
			
		} catch (fallbackErr) {
			console.error('Failed to copy CIDR to clipboard:', fallbackErr);
			
			// Show error feedback
			copyButton.style.backgroundColor = '#dc3545';
			copyButton.innerHTML = '<i class="fas fa-times"></i>';
			
			// Reset button after 2 seconds
			setTimeout(() => {
				copyButton.style.backgroundColor = '';
				copyButton.innerHTML = '<i class="fas fa-copy"></i>';
			}, 2000);
		}
	}
}