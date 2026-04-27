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
          <select>
            <option>All issues</option>
            <option>Future issues</option>
            <option>Recent issues</option>
            <option>First volume</option>
            <option>Last volume</option>
            <option>None</option>
          </select>
        </div>
        <div class="form-item">
          <label>Format</label>
          <select>
            <option>CBZ</option>
            <option>CBZ</option>
            <option>PDF</option>
          </select>
        </div>
        <div class="form-item">
          <label>Volume folder</label>
          <input type="checkbox" class="checkbox" />
        </div>
        <div class="form-item">
          <label>Tags</label>
          <input class="text-input" />
          <span>Comma-seperated tags</span>
        </div>
      </div>
    </div>
    <div class="footer">
      <div class="input">
        Start search for missing issues
        <input type="checkbox" />
      </div>
      <button class="active" onClick="toggleLoading()">
        <span id="button-text">Add comic</span>
        <div id="button-spinner" style="display: none"></div>
      </button>
    </div>
  </div>
</div>
  `
}



function toggleLoading(){
  document.getElementById("button-text").style.display = "none";
  document.getElementById("button-spinner").style.display = "block";
}

async function showComicDetailPopup(data, media_path) {
  const container = document.getElementById("content");
  container.innerHTML += formatPopup(data, media_path);
}


function hidePopup() {
  const popup = document.getElementById("popup-container");
  popup.parentNode.removeChild(popup);
}

