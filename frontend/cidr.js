async function get_cidr() {
	const subnet_size = document.getElementById('subnet')?.value || '';
	const requiredrange = document.getElementById('range')?.value || '';
	const reason = document.getElementById('reason')?.value || '';

	const url = `/get-cidr?subnet_size=${subnet_size}&requiredrange=${requiredrange}&reason=${reason}`;

	try {
		document.getElementById('cidr').value = "Retrieving unigue cidr..";
		const response = await fetch(url);
		const cidrRes = await response.text();
		document.getElementById('cidr').value = (cidrRes);
	}
	catch (e) {
		document.getElementById('cidr').value = `server error: ${e.message}`;
	}
}

async function get_occupied_list() {
	const url = `/get-occupied-list`;
	try {
		document.getElementById('cidrlist').value = "Trying to obtain list from GIT repo..";
		const response = await fetch(url);
		const occupiedlist = await response.text();
		document.getElementById('json-output').innerHTML = occupiedlist;
		document.getElementById('cidrlist').value = "Done!";
	}
	catch (e) {
		document.getElementById('cidrlist').value = `server error: ${e.message}`;
	}
}
