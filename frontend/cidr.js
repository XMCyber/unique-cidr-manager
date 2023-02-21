async function get_cidr() {
	const subnet_size = document.getElementById('subnet')?.value || '';
	const requiredrange = document.getElementById('range')?.value || '';
	const reason = document.getElementById('reason')?.value || '';

	const url = `/get-cidr?subnet_size=${subnet_size}&requiredrange=${requiredrange}&reason=${reason}`;

	try {
		document.getElementById('cidr_messages').innerHTML = "Retrieving unigue cidr..";
		const response = await fetch(url);
		const cidrRes = await response.text();
		document.getElementById('cidr_output').innerHTML = (cidrRes);
		document.getElementById('cidr_messages').innerHTML = "Done!";

	}
	catch (e) {
		document.getElementById('cidr_messages').innerHTML = `server error: ${e.message}`;
	}
}

async function get_occupied_list() {
	const url = `/get-occupied-list`;
	try {
		document.getElementById('occupied_messages').innerHTML = "Trying to obtain list from GIT repo..";
		const response = await fetch(url);
		const occupiedlist = await response.text();
		document.getElementById('occupied_output').innerHTML = occupiedlist;
		document.getElementById('occupied_messages').innerHTML = "Done!";
	}
	catch (e) {
		document.getElementById('occupied_messages').innerHTML = `server error: ${e.message}`;
	}
}

async function get_next_cidr() {
	const subnet_size = document.getElementById('subnet')?.value || '';
	const requiredrange = document.getElementById('range')?.value || '';
	const reason = document.getElementById('reason')?.value || '';

	const url = `/get-next-cidr-no-push?subnet_size=${subnet_size}&requiredrange=${requiredrange}&reason=${reason}`;
	try {
		document.getElementById('cidr_messages').innerHTML = "Trying to obtain list from GIT repo..";
		const response = await fetch(url);
		const occupiedlist = await response.text();
		document.getElementById('cidr_output').innerHTML = occupiedlist;
		document.getElementById('cidr_messages').innerHTML = "Done!";
	}
	catch (e) {
		document.getElementById('cidr_messages').innerHTML = `server error: ${e.message}`;
	}
}

async function delete_cidr_from_list() {
	const cidr_deletion = document.getElementById('cidr_deletion')?.value || '';

	const url = `/delete-cidr-from-list?cidr_deletion=${cidr_deletion}`;
	try {
		document.getElementById('delete_messages').innerHTML = "Trying to obtain list from GIT repo..";
		const response = await fetch(url);
		const occupiedlist = await response.text();
		document.getElementById('delete_messages').innerHTML = occupiedlist;
	}
	catch (e) {
		document.getElementById('delete_messages').innerHTML = `server error: ${e.message}`;
	}
}