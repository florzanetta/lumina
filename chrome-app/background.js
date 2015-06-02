chrome.app.runtime.onLaunched.addListener(function() {
  chrome.app.window.create('window.html', {
    'bounds': {
      'width': 400,
      'height': 500
    }
  });
});

chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    console.info("request: " + request + " - username: " + request['username']);
    // console.info("sender: " + sender);
  });

console.info("Load finished");
