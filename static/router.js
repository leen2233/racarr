let currentModules = [];

async function navigate(url) {
  window.history.pushState({}, "", url);
  makeCurrentNavActive();

  const container = document.getElementById("content");
  currentModules.forEach((mod) => {
    mod.destroy?.(container);
  });
  currentModules = [];

  // load html
  const r = await fetch(url, {
    method: "GET",
    headers: {
      "X-Partial-Content": true,
    },
  });

  const html = await r.text();
  container.innerHTML = html;

  const jsPathElems = container.querySelectorAll(".jsPath");
  const arr = Array.from(jsPathElems);
  const imports = arr.map(async (jsPathElem) => {
    const jsPath = jsPathElem.dataset.js;
    const mod = await import(jsPath);
    currentModules.push(mod);

    mod.init(container);
  });

  await Promise.all(imports);
}

document.addEventListener("DOMContentLoaded", makeCurrentNavActive);

async function makeCurrentNavActive() {
  // Load js for active page
  const container = document.querySelector("#content");
  const jsPathElems = container.querySelectorAll(".jsPath");
  const arr = Array.from(jsPathElems);
  const imports = arr.map(async (jsPathElem) => {
    const jsPath = jsPathElem.dataset.js;
    const mod = await import(jsPath);
    currentModules.push(mod);

    mod.init(container);
  });

  await Promise.all(imports);

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
