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

	/**
	 * @public
	 */
	pingLumina : function() {
		var req = new XMLHttpRequest();
		// http://www.w3.org/TR/XMLHttpRequest/
		req.open("GET", "http://127.0.0.1:8000/rest/ping", true);
		req.onload = this.showPingResponse_.bind(this);
		req.onerror = this.xmlhttprequesterror_.bind(this);
		console.debug("eventPage.js: will send XMLHttpRequest")
		req.send(null);
		console.debug("eventPage.js: XMLHttpRequest sent")
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
		} else {
			set_log("Connection to server ok. Remember to login!");
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
	}
});

// Create the alarm:
chrome.alarms.create('lumina-poll', {
	periodInMinutes : 1.0 / 3.0, // 20 secs
});

chrome.alarms.create('lumina-poll-initial', {
	delayInMinutes : 1.0 / 30.0, // 2 secs
});

console.info("eventPage.js: end");
