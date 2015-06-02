//
// Event Page
//  - http://developer.chrome.com/extensions/event_pages.html
//

console.info("eventPage.js: start");

function set_log(msg) {
	chrome.storage.local.set({
		'log_msg' : msg
	}, function() {
		if (chrome.runtime.lastError) {
			console.error("set_log(): error when trying to save msg: "
					+ chrome.runtime.lastError);
		} else {
			console.debug("set_log(): saved!");
		}
	});
}

function get_last_log(callback) {
	return chrome.storage.local.get('log_msg', callback);
}

var luminaService = {

	getObjectFromXMLHttpResponse: function(response) {
		// FIXME: handle exceptions!
		var resp = JSON.parse(response.target.responseText);
		return resp;
	},

	sendMessageToLuminaApp: function(message) {
		/*
		 * https://developer.chrome.com/extensions/runtime#method-sendMessage
		 */
		var extensionId = "decjfgeckpkpgilljbjmmballhljnogf";
		chrome.runtime.sendMessage(extensionId, message);
		console.debug("Message sent to Lumina App");
	},

	/**
	 * @public
	 */
	pingLumina : function() {
		var req = new XMLHttpRequest();
		// http://www.w3.org/TR/XMLHttpRequest/
		req.open("GET", "http://localhost:8000/rest/ping", true);
		req.onload = this.showPingResponse_.bind(this);
		req.onerror = this.xmlhttprequesterror_.bind(this);
		console.debug("eventPage.js: will send XMLHttpRequest")
		req.send(null);
		console.debug("eventPage.js: XMLHttpRequest sent");
	},

	/**
	 * @param {ProgressEvent}
	 *            e The XHR ProgressEvent.
	 * @private
	 */
	showPingResponse_ : function(e) {
		// e.target.responseXML.querySelectorAll('photo');
		var resp = JSON.parse(e.target.responseText);
		var msg = '' + resp['status'] + " / " + resp['server_date_str']
				+ " / '" + resp['username'] + "'";
		console.debug("eventPage.js: Server returned: " + msg);
		if ('username' in resp && resp['username'].length > 0) {
			set_log("User '" + resp['username'] + "' logged in");
			console.info("eventPage.js: User is logged in");
			this.sendMessageToLuminaApp({username: resp['username']});
		} else {
			set_log("Connection to server ok. Remember to login!");
			console.info("eventPage.js: Connection to server ok. User is NOT logged in");
			this.sendMessageToLuminaApp({username: ''});
		}

		chrome.browserAction.setIcon({
			path : 'glyphicons_232_cloud.png'
		});
	},

	xmlhttprequesterror_ : function(e) {
		console.error("eventPage.js: XMLHttpRequest ERROR: '" + e + "' - "
				+ e.target.status);
		set_log("Couldn't connect to server");
		chrome.browserAction.setIcon({
			path : 'glyphicons_413_cloud_minus.png'
		});
	},

	//
	// check_pending_uploads
	//

	/**
	 * @public
	 */
	checkForPendingUploads : function() {
		var req = new XMLHttpRequest();
		// http://www.w3.org/TR/XMLHttpRequest/
		req.open("GET", "http://localhost:8000/rest/check_pending_uploads",
				true);
		req.onload = this.checkForPendingUploadsCallback.bind(this);
		req.onerror = this.checkForPendingUploadsCallbackError.bind(this);
		console.debug("eventPage.js: will send XMLHttpRequest")
		req.send(null);
		console.debug("eventPage.js: XMLHttpRequest sent")
	},

	checkForPendingUploadsCallback : function(e) {
		var resp = this.getObjectFromXMLHttpResponse(e);
		if(resp['status'] != 'ok') {
			console.error("checkForPendingUploadsCallback(): Status != OK - status: '" + resp['status']  + "'");
			// FIXME: do something else beyond logging by console!
			return;
		}
			
		if(! ('pending_uploads_count' in resp)) {
			console.error("checkForPendingUploadsCallback(): 'pending_uploads_count' not in response");
			// FIXME: do something else beyond logging by console!
			return;
		}
		
		if (resp['pending_uploads_count'] > 0) {
			console.info("HAY UPLOADS PENDIENTES! - pending_uploads_count: " + resp['pending_uploads_count']);
		} else {
			console.info("No hay uploads pendientes");
		}

	},

	checkForPendingUploadsCallbackError : function(e) {
		console.error("checkForPendingUploadsCallbackError()");
	}

// http://stackoverflow.com/questions/4093722/upload-a-file-in-a-google-chrome-extension

};

chrome.runtime.onSuspend.addListener(function() {
	console.info("eventPage.js: onSuspend()");
});

chrome.runtime.onStartup.addListener(function() {
	console.info("eventPage.js: onStartup()");
});

chrome.alarms.onAlarm.addListener(function(alarm) {
	if (alarm.name == 'lumina-poll' || alarm.name == 'lumina-poll-initial') {
		console.debug("eventPage.js: onAlarm(" + alarm.name + ")");
		luminaService.pingLumina();
		return;
	}

	if (alarm.name == 'lumina-poll-pending-uploads') {
		console.debug("eventPage.js: onAlarm(" + alarm.name + ")");
		luminaService.checkForPendingUploads();
		return;
	}

});

// Create the alarm:
chrome.alarms.create('lumina-poll', {
	periodInMinutes : 1.0 / 3.0, // 20 secs
});

chrome.alarms.create('lumina-poll-initial', {
	delayInMinutes : 1.0 / 30.0, // 2 secs
});

chrome.alarms.create('lumina-poll-pending-uploads', {
	periodInMinutes : 1.0 / 3.0, // 20 secs
});

console.info("eventPage.js: end");
