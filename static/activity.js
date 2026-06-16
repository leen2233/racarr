function streamActivityEvent() {
  const el = document.getElementById("activity-table");
  if (!el) return;

  if (typeof EventSource !== "undefined") {
    var source = new EventSource("/api/events/activity");
    source.onmessage = function (event) {
      var data = JSON.parse(event.data);
      var row = document.getElementById(data.queue_id);
      if (!row) {
        return;
      }
      if (data.status == "downloading") {
        row.querySelector(".status").innerHTML =
          `Downloading (${data.progress}%)`;
        return;
      } else if (data.status == "error") {
        row.querySelector(".status").innerHTML = "Error";
      } else if (data.status == "completed") {
        row.parentNode.removeChild(row);
      }
    };
  } else {
    console.log("Sorry, your browser does not support server-sent events...");
  }
}

document.addEventListener("content:loaded", function () {
  streamActivityEvent();
});

document.addEventListener("DOMContentLoaded", function () {
  streamActivityEvent();
});
