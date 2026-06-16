function streamNotifications() {
  if (typeof EventSource !== "undefined") {
    var notificationsDiv = document.getElementById("notifications");
    var source = new EventSource("/api/events/notifications");
    source.onmessage = function (event) {
      var data = JSON.parse(event.data);
      var randomID = Math.random() * 1000000;
      notificationsDiv.innerHTML += `<div class='notification ${data.type}' id='${randomID}'>${data.text}</div>`;
      setTimeout(function () {
        hideNotification(randomID);
      }, 5000);
    };
  } else {
    console.log("Sorry, your browser does not support server-sent events...");
  }
}

function hideNotification(id) {
  const notification = document.getElementById(id);
  notification.parentNode.removeChild(notification);
}
