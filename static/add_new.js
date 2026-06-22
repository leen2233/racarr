export function init(container) {
  bindEvents(container);

  const el = container.querySelector("#search-comics-container");

  if (el.dataset.initialized == "0") {
    handleSearch(container);
  }
}

export function destroy(container) {
  container.removeEventListener("keypress", handleKeyPress);
  container.removeEventListener("click", handleClick);
}

function bindEvents(container) {
  container.addEventListener("keypress", handleKeyPress);
  container.addEventListener("click", handleClick);
}

function handleClick(e) {
  if (e.target.matches("#handleSearch")) {
    handleSearch(e.currentTarget);
  } else if (e.target.matches("#clearInput")) {
    clearInput(e.currentTarget);
  }
}

function handleKeyPress(e) {
  if (e.target.matches("#searchInput") && e.key === "Enter") {
    e.preventDefault();
    handleSearch(e.currentTarget);
  }
}

function clearInput(container) {
  container.querySelector("#query").value = "";
}

async function handleSearch(container) {
  changeQuery(container);

  const query = container.querySelector("#searchInput").value;
  const source = container.querySelector("#source").value;
  container.querySelector("#search-helper").style.display = "none";
  container.querySelector("#error").style.display = "none";
  container.querySelector("#search-comics-container").innerHTML = "";
  container.querySelector("#loading").style.display = "block";

  if (query == "") {
    container.querySelector("#loading").style.display = "none";
    return;
  }

  const url = "/api/search-remote?query=" + query + "&source=" + source;
  try {
    const response = await fetch(url);
    container.querySelector("#loading").style.display = "none";

    const result = await response.json();

    if (!response.ok) {
      container.querySelector("#error").style.display = "block";
      throw new Error(result.error);
    }

    const search_container = container.querySelector(
      "#search-comics-container",
    );
    search_container.innerHTML = "";
    var html = "";
    const mediaPath = search_container.dataset.mediaPath;

    result.forEach((item) => {
      var itemJson = JSON.stringify(item)
        .replace("'", "&apos;")
        .replace('"', "&quot;");

      html += `
          <div class="search-comic-item" id="showAddComicPopup" data-item='${itemJson}' data-media-path="${mediaPath}">
            <img src="${item.cover}" loading='lazy'>
            <div class="search-comic-data">
              <div class="title-row">
                <div class="title">${item.name} <span>(${item.year})</span></div>
                <a href="${item.url}" target="_blank"><i class="fa fa-external-link"></i></a>
              </div>
              <div class="info-row">
                <div class="info"><i class="fa fa-tags"></i>${formatGenres(item.genres)}</div>
                <div class="info"><i class="fa fa-building"></i>${item.publisher}</div>
                <div class="info"><i class="fa fa-files-o"></i>${item.total_issues} issues</div>
              </div>
            </div>
          </div>
        `;
    });
    search_container.innerHTML = html;
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

function changeQuery(container) {
  const source = container.querySelector("#source").value;
  const query = container.querySelector("#searchInput").value;
  const url = new URL(window.location);

  url.searchParams.set("source", source);
  url.searchParams.set("query", query);
  window.history.pushState({}, "", url);
}
