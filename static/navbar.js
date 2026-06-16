function getAndChange(url) {
  window.history.pushState({}, "", url);
  makeCurrentNavActive();

  fetch(url, {
    method: "GET",
    headers: {
      "X-Partial-Content": true,
    },
  })
    .then((r) => r.text())
    .then((html) => {
      document.querySelector("#content").innerHTML = html;
      document.dispatchEvent(new Event("content:loaded"));
    });
}

document.addEventListener("DOMContentLoaded", makeCurrentNavActive);

function makeCurrentNavActive() {
  // Set current navbar group  active
  let path = window.location.pathname;

  let groups = document.querySelectorAll(".navbar-group");
  groups.forEach((element) => element.classList.remove("active"));

  if (
    path == "/" ||
    path == "/add" ||
    path == "/discover" ||
    path.startsWith("/comic/")
  ) {
    document.getElementById("home").classList.add("active");
  }
  if (path == "/activity") {
    document.getElementById("activity").classList.add("active");
  }
  if (path == "/settings") {
    document.getElementById("settings").classList.add("active");
  }

  // Set current navbar item active
  let items = document.querySelectorAll(".navbar-item");
  items.forEach((element) => element.classList.remove("active"));

  if (path == "/") {
    document.getElementById("home-home").classList.add("active");
  }
  if (path == "/add") {
    document.getElementById("home-add-new").classList.add("active");
  }
  if (path == "/discover") {
    document.getElementById("home-discover").classList.add("active");
  }
  if (path == "/activity") {
    document.getElementById("activity-activity").classList.add("active");
  }
  if (path == "/settings") {
    document.getElementById("settings-general").classList.add("active");
  }
}
