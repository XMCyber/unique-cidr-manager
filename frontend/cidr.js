async function onSubmit() {
	const subnet_size = document.getElementById('subnet')?.value || '';
	const requiredrange = document.getElementById('range')?.value || '';
	const reason = document.getElementById('reason')?.value || '';

	if (subnet_size.length  && requiredrange.length  && reason.length) {
		document.getElementById('cidr').value = "Obtaining CIDR from pool";
	} else {
		document.getElementById('cidr').value = "Please fill all the fields";
		return
	}

	const url = `/get-cidr?subnet_size=${subnet_size}&requiredrange=${requiredrange}&reason=${reason}`;

	try {
		const response = await fetch(url);
		const cidrRes = await response.text();
		document.getElementById('cidr').value = (cidrRes);
	}
	catch (e) {
		document.getElementById('cidr').value = `server error: ${e.message}`;
	}
}