async function onSubmit() {
	const subnet_size = document.getElementById('subnet')?.value || '';
	const requiredrange = document.getElementById('range')?.value || '';
	const reason = document.getElementById('reason')?.value || '';

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
