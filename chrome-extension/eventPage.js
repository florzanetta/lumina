//
// Event Page
//  - http://developer.chrome.com/extensions/event_pages.html
//

console.info("eventPage.js: start");

/*
 * chrome.runtime.onStartup.addListener(function() { document.body.innerHTML += "<p>EVENTPAGE ->
 * onStartup()</p>"; console.info("EVENTPAGE -> onStartup()"); });
 */

/*
 * var notification = webkitNotifications.createNotification('icon.png',
 * 'Hello!', 'Lorem ipsum...'); // Or create an HTML notification: var
 * notification = webkitNotifications
 * .createHTMLNotification('notification.html'); // Then show the notification.
 * notification.show();
 */

var luminaService = {
	//
	// THIS HAS BEEN CPOPIED-AND-PASTED FROM popup.js!
	// FIXME: IMPORT CODE FROM popup.js
	//

	/**
	 * @public
	 */
	pingLumina : function() {
		var req = new XMLHttpRequest();
		// http://www.w3.org/TR/XMLHttpRequest/
		req.open("GET", "http://127.0.0.1:8000/rest/ping", true);
		req.onload = this.showPingResponse_.bind(this);
		req.onerror = this.xmlhttprequesterror_.bind(this);
		console.info("eventPage.js: will send XMLHttpRequest")
		req.send(null);
		console.info("eventPage.js: XMLHttpRequest sent")
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
		console.info("eventPage.js: Server returned: " + msg);
	},

	xmlhttprequesterror_ : function(e) {
		console.error("eventPage.js: XMLHttpRequest ERROR: '" + e + "' - "
				+ e.target.status);
	}

// http://stackoverflow.com/questions/4093722/upload-a-file-in-a-google-chrome-extension

};

chrome.alarms.onAlarm.addListener(function(alarm) {
	if (alarm.name == 'lumina-poll' || alarm.name == 'lumina-poll-initial') {
		console.info("eventPage.js: onAlarm(" + alarm.name + ")");
		luminaService.pingLumina();
	}
});

// Create the alarm:
chrome.alarms.create('lumina-poll', {
	periodInMinutes : (1.0) / 12.0, // 10 secs
});

chrome.alarms.create('lumina-poll-initial', {
	delayInMinutes : 0.001,
});

console.info("eventPage.js: end");
