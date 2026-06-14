function getAndChange(url) {
  window.history.pushState({}, "", url);

  fetch(url, {
      method: "GET",
      headers: {
        "X-Partial-Content": true,
      }
  })
    .then(r => r.text())
    .then(html => {
      document.querySelector("#content").innerHTML = html;
      document.dispatchEvent(new Event("content:loaded"))
    })
}

