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
		const response = await fetch(url);
		const cidrRes = await response.text();
		document.getElementById('cidr_output').innerHTML = (cidrRes);
		document.getElementById('cidr_messages').innerHTML = "Done!";

	}
	catch (e) {
		document.getElementById('cidr_messages').innerHTML = `Server error: ${e.message}`;
		document.getElementById('cidr_output').innerHTML = error_message;
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
	  
	  const num_elements = Object.keys(originalOccupiedData).length;
	  document.getElementById('occupied_messages').innerHTML = `Done! Raw count is ${num_elements}`;
	  
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
		const response = await fetch(url);
		const occupiedlist = await response.text();
		document.getElementById('cidr_output').innerHTML = occupiedlist;
		document.getElementById('cidr_messages').innerHTML = "Done!";
	}
	catch (e) {
		document.getElementById('cidr_messages').innerHTML = `Server error: ${e.message}`;
		document.getElementById('cidr_output').innerHTML = error_message;

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
	let formattedOutput = '';
	
	if (Object.keys(data).length === 0) {
		formattedOutput = 'No occupied CIDR blocks found.';
	} else {
		// Create a formatted display with reason and CIDR
		for (const [key, cidr] of Object.entries(data)) {
			// Extract reason by removing the timestamp suffix
			const reason = key.replace(/-\d+$/, '');
			formattedOutput += `Reason: ${reason}\nCIDR: ${cidr}\n\n`;
		}
	}
	
	document.getElementById('occupied_output').innerHTML = formattedOutput;
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
		const totalCount = Object.keys(originalOccupiedData).length;
		document.getElementById('occupied_messages').innerHTML = `Done! Raw count is ${totalCount}`;
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
	const totalCount = Object.keys(originalOccupiedData).length;
	document.getElementById('occupied_messages').innerHTML = `Showing ${matchCount} of ${totalCount} CIDR blocks`;
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