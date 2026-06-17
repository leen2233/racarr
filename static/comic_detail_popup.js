export function init(container) {
  bindEvents(container);
}

export function destroy(container) {
  container.removeEventListener("click", handleClick);
}

function bindEvents(container) {
  container.addEventListener("click", handleClick);
}

function handleClick(e) {
  const item = e.target.closest(".search-comic-item");
  const addButton = e.target.closest("#addComic");
  if (item) {
    showAddComicPopup(e.currentTarget, item);
  } else if (e.target.matches("#closePopup")) {
    closePopup(e.currentTarget);
  } else if (addButton) {
    addComic(e.currentTarget, addButton);
  }
}

function formatPopup(data, media_path) {
  return `
<div id="popup-container">
  <div class="popup">
    <div class='header'>
      <div>${data.name} (${data.year})</div>
      <i class="fa fa-times" id="closePopup"></i>
    </div>
    <div class="popup-content">
      <div class="img"><img src="${data.cover}" /></div>
      <div class="form">
        <div class="form-item">
          <label>Root Folder</label>
          <select>
            <option>${media_path}/${data.name}</option>
          </select>
          <span>${data.name} subfolder will be created automatically</span>
        </div>
        <div class="form-item">
          <label>Monitor</label>
          <select id="monitor">
            <option value="all">All issues</option>
            <option value="future">Future issues</option>
            <option value="past">Past issues</option>
            <option value="first">First volume</option>
            <option value="last">Last volume</option>
            <option value="none">None</option>
          </select>
        </div>
        <div class="form-item">
          <label>Format</label>
          <select id="format">
            <option value="cbz">CBZ</option>
            <option value="cbr">CBR</option>
            <option value="pdf">PDF</option>
          </select>
        </div>
        <div class="form-item">
          <label>Volume folder</label>
          <input type="checkbox" class="checkbox" id="volume_folder" />
        </div>
        <div class="form-item">
          <label>Tags</label>
          <input class="text-input" id="tags" />
          <span>Comma-seperated tags</span>
        </div>
      </div>
    </div>
    <div class="footer">
      <div class="input">
        Start search for missing issues
        <input type="checkbox" id="search_missing" />
      </div>
      <button class="active" id="addComic" data-id='${data.id}'>
        <span id="button-text">Add comic</span>
        <div id="button-spinner" style="display: none"></div>
      </button>
    </div>
  </div>
</div>
  `;
}

async function addComic(container, el) {
  container.querySelector("#button-text").style.display = "none";
  container.querySelector("#button-spinner").style.display = "block";
  const csrfToken = getCookie("csrftoken");
  const id = el.dataset.id;

  const monitor = container.querySelector("#monitor").value;
  const format = container.querySelector("#format").value;
  const volume_folder = container.querySelector("#volume_folder").checked;
  const tags = container.querySelector("#tags").value;
  const search_missing = container.querySelector("#search_missing").checked;

  const data = {
    monitor: monitor,
    format: format,
    volume_folder: volume_folder,
    tags: tags,
    id: id,
    search_missing: search_missing,
  };
  try {
    const response = await fetch("/api/comic", {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    });
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const result = await response.json();
    document.location.href = result.url;
  } catch (error) {
    console.error(error.message);
  }
}

async function showAddComicPopup(container, el) {
  let data = JSON.parse(el.dataset.item);
  let mediaPath = el.dataset.mediaPath;
  container.innerHTML += formatPopup(data, mediaPath);
}

function closePopup(container) {
  const popup = container.querySelector("#popup-container");
  popup.parentNode.removeChild(popup);
}
