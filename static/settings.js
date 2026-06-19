export function init(container) {
  bindEvents(container);
}

export function destroy(container) {
  container.removeEventListener("change", handleChange);
  container.removeEventListener("click", handleClick);
}

function bindEvents(container) {
  container.addEventListener("change", handleChange);
  container.addEventListener("click", handleClick);
}

function handleChange(e) {
  valueChanged(e.currentTarget);
}

function handleClick(e) {
  const saveButton = e.target.closest("#saveChanges");
  if (saveButton) {
    saveSettings(e.currentTarget, saveButton);
  }
}

function valueChanged(container) {
  let changed = false;
  container.querySelectorAll(".input").forEach((input) => {
    var currentValue = input.value;
    if (input.id == "useProxy") {
      currentValue = input.checked.toString();
    }
    if (input.dataset.initial != currentValue) {
      changed = true;
    }
  });

  if (changed) {
    container.querySelector("#saveChanges").classList.remove("disabled");
    container.querySelector("#save-button-text").innerHTML = "Save";
  } else {
    container.querySelector("#saveChanges").classList.add("disabled");
    container.querySelector("#save-button-text").innerHTML = "No Changes";
  }
}

async function saveSettings(container, el) {
  if (el.classList.contains("disabled")) {
    return;
  }
  const csrfToken = getCookie("csrftoken");

  const data = {
    use_proxy: container.querySelector("#useProxy").checked,
    proxy_type: container.querySelector("#proxyType").value,
    proxy_host: container.querySelector("#proxyHost").value,
    proxy_port: container.querySelector("#proxyPort").value,
    proxy_username: container.querySelector("#proxyUsername").value,
    proxy_password: container.querySelector("#proxyPassword").value,
  };

  try {
    const response = await fetch("/api/settings", {
      method: "PATCH",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    });
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    container.querySelector("#saveChanges").classList.add("disabled");
    container.querySelector("#save-button-text").innerHTML = "No Changes";

    // set initials
    container.querySelectorAll(".input").forEach((input) => {
      var currentValue = input.value;
      if (input.id == "useProxy") {
        currentValue = input.checked.toString();
      }
      input.dataset.initial = currentValue;
    });
  } catch (error) {
    console.error(error.message);
  }
}
