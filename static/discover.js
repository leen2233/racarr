export function init(container) {
  bindEvents(container);

  const el = container.querySelector("#discover-container");
  if (el.dataset.initialized == "1") {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  var source = params.get("source");
  if (!source) {
    source = el.dataset.defaultSource;
  }

  fetchDiscoverData(container, source);
}

export function destroy(container) {
  container.removeEventListener("click", handleClick);
}

function bindEvents(container) {
  container.addEventListener("click", handleClick);
}

function handleClick(e) {
  if (e.target.matches("#changeSource")) {
    changeSource(e.currentTarget);
  }
}

async function fetchDiscoverData(container, source) {
  container.querySelector("#loading").style.display = "block";
  container.querySelector("#error").style.display = "none";
  const discover_container = container.querySelector("#discover-container");
  discover_container.innerHTML = "";

  const url = "/api/discover?source=" + source;
  try {
    const response = await fetch(url);
    container.querySelector("#loading").style.display = "none";

    const result = await response.json();

    if (!response.ok) {
      container.querySelector("#error").style.display = "block";
      throw new Error(result.error);
    }
    var html = "";
    result.forEach((item) => {
      html += `
        <div class="discover-item">
          <img src="${item.cover}" loading='lazy'>
          <div>
            <h3>${item.name}</h3>
            <div class="info-container">
              <div class="info"><i class="fa fa-calendar"></i>${item.year}</div>
              <div class="info"><i class="fa fa-building"></i>${item.publisher}</div>
              <div class="info"><i class="fa fa-tags"></i>${formatGenres(item.genres)}</div>
              <div class="info"><i class="fa fa-files-o"></i>${item.total_issues} issues</div>
            </div>
          </div>
        </div>
      `;
    });
    discover_container.innerHTML = html;
  } catch (error) {
    container.querySelector("#error-message").innerHTML = error;
    console.error(error);
  }
}

function formatGenres(value) {
  let text = value[0];
  for (let i = 1; i < value.length; i++) {
    text += `, ${value[i]}`;
  }
  return text;
}

function changeSource(container) {
  const source = container.querySelector("#source").value;
  const url = new URL(window.location);

  url.searchParams.set("source", source);
  window.history.pushState({}, "", url);

  fetchDiscoverData(container, source);
}
