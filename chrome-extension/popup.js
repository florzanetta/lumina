// Run our kitten generation script as soon as the document's DOM is ready.

function set_status(result) {
	var status = document.getElementById('status');
	status.textContent = result.log_msg;
};

document.addEventListener('DOMContentLoaded', function() {
	var msg = document.createElement('h1');
	msg.textContent = "Lumina";
	document.body.appendChild(msg);

	var status = document.createElement('div');
	status.setAttribute("id", "status");
	status.textContent = "";
	document.body.appendChild(status);

	// http://developer.chrome.com/extensions/runtime.html#method-getBackgroundPage
	chrome.runtime.getBackgroundPage(function(backgroundPageWindow) {
		console.info("Last log: "
				+ backgroundPageWindow.get_last_log(set_status));
	});

});
