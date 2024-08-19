const git_message = 'Trying to obtain list from GIT repo';
const wait_message = 'Please wait..';
const error_message = 'Failed, please try again';

async function get_cidr() {
	const subnet_size = document.getElementById('subnet')?.value || '';
	const requiredrange = document.getElementById('range')?.value || '';
	const reason = document.getElementById('reason')?.value || '';

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
	try {
	  document.getElementById('occupied_messages').innerHTML = git_message;
	  document.getElementById('occupied_output').innerHTML = wait_message;
	  const response = await fetch(url);
	  const occupiedlist = await response.text();
	  document.getElementById('occupied_output').innerHTML = occupiedlist;
	  const num_elements = Object.keys(JSON.parse(occupiedlist)).length; // Counting elements in the object
	  document.getElementById('occupied_messages').innerHTML = `Done! Raw count is ${num_elements}`;
	} catch (e) {
	  document.getElementById('occupied_messages').innerHTML = `Server error: ${e.message}`;
	  document.getElementById('occupied_output').innerHTML = error_message;
	}
}

async function get_next_cidr() {
	const subnet_size = document.getElementById('subnet')?.value || '';
	const requiredrange = document.getElementById('range')?.value || '';
	const reason = document.getElementById('reason')?.value || '';

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