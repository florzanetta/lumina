var luminaService = {

	/**
	 * @public
	 */
	pingLumina : function() {
		var req = new XMLHttpRequest();
		// http://www.w3.org/TR/XMLHttpRequest/
		req.open("GET", "http://127.0.0.1:8000/rest/ping", true);
		req.onload = this.showPingResponse_.bind(this);
		req.send(null);
	},

	/**
	 * @param {ProgressEvent}
	 *            e The XHR ProgressEvent.
	 * @private
	 */
	showPingResponse_ : function(e) {
		// e.target.responseXML.querySelectorAll('photo');
		var resp = JSON.parse(e.target.responseText);
		var msg = document.createElement('p');
		msg.textContent = '' + resp['status'] + " / " + resp['server_date_str']
				+ " / '" + resp['username'] + "'";
		document.body.appendChild(msg);
	},

	// http://stackoverflow.com/questions/4093722/upload-a-file-in-a-google-chrome-extension
};

// Run our kitten generation script as soon as the document's DOM is ready.
document.addEventListener('DOMContentLoaded', function() {
	luminaService.pingLumina();
});
