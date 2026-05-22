function formatPopup(data, media_path) {
  return `
<div id="popup-container">
  <div class="popup">
    <div class='header'>
      <div>${data.name} (${data.year})</div>
      <i class="fa fa-times" onClick="hidePopup()"></i>
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
        <input type="checkbox" />
      </div>
      <button class="active" onClick="addComic('${data.id}')">
        <span id="button-text">Add comic</span>
        <div id="button-spinner" style="display: none"></div>
      </button>
    </div>
  </div>
</div>
  `
}


async function addComic(id){
  document.getElementById("button-text").style.display = "none";
  document.getElementById("button-spinner").style.display = "block";
  const csrfToken = getCookie("csrftoken")

  const monitor = document.getElementById("monitor").value;
  const format  = document.getElementById("format").value;
  const volume_folder = document.getElementById("volume_folder").checked;
  const tags = document.getElementById("tags").value;

  const data = {monitor: monitor, format: format, volume_folder: volume_folder, tags: tags, id: id};
  try {
    const response = await fetch("/api/add-comic", {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      }
    })
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const result = await response.json();
    document.location.href = result.url;
  } catch (error) {
    console.error(error.message);
  }

}

async function showComicDetailPopup(data, media_path) {
  const container = document.getElementById("content");
  container.innerHTML += formatPopup(data, media_path);
}


function hidePopup() {
  const popup = document.getElementById("popup-container");
  popup.parentNode.removeChild(popup);
}


