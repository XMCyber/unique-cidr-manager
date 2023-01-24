
async function sendToServer(subnet_size, requiredrange, reason) {

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

function onSubmit() {

	const userMsg = document.getElementById('cidr');
	userMsg.value = "";

	const subnet_size = document.getElementById('subnet')?.value || '';
	const requiredrange = document.getElementById('range')?.value || '';
	const reason = document.getElementById('reason')?.value || '';

	if (subnet_size.length  && requiredrange.length  && reason.length) {
		console.log("sending to server")
		sendToServer(subnet_size, requiredrange, reason);
	} else {
		userMsg.value = "Please fill in all the fileds..."
	}
}
