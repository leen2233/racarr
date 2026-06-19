export function init(container) {
  bindEvents(container);
  streamActivityEvent(container);
}

export function destroy(container) {
  container.removeEventListener("click", handleClick);

  if (container._eventSource) {
    container._eventSource.close();
    delete container._eventSource;
  }
}

function bindEvents(container) {
  container.addEventListener("click", handleClick);
}

function handleClick(e) {
  const retryItem = e.target.closest("#retryItem");
  const deleteItem = e.target.closest("#deleteItem");
  if (retryItem) {
    retryQueueItem(e.currentTarget, retryItem);
  } else if (deleteItem) {
    deleteQueueItem(e.currentTarget, deleteItem);
  }
}

function streamActivityEvent(container) {
  const el = container.querySelector("#activity-table");
  if (!el) return;

  if (typeof EventSource !== "undefined") {
    const source = new EventSource("/api/events/activity");
    container._eventSource = source;

    source.onmessage = function (event) {
      var data = JSON.parse(event.data);
      var row = container.querySelector("#item" + data.queue_id);
      if (!row) {
        return;
      }
      if (data.status == "downloading") {
        row.querySelector(".status").innerHTML =
          `Downloading (${data.progress}%)`;
        return;
      } else if (data.status == "error") {
        row.querySelector(".status").innerHTML =
          `Error <div class="error-message">${data.error_message}</div>`;
      } else if (data.status == "completed") {
        row.parentNode.removeChild(row);
      }
    };
  } else {
    console.log("Sorry, your browser does not support server-sent events...");
  }
}

async function retryQueueItem(container, el) {
  el.classList.remove("fa-repeat");
  el.classList.add("fa-spinner");

  const id = el.dataset.id;
  const csrfToken = getCookie("csrftoken");
  const url = "/api/retry-queue-item";
  try {
    const response = await fetch(url, {
      method: "POST",
      body: JSON.stringify({ id: id }),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error);
    }

    el.classList.remove("fa-spinner");
    el.classList.add("fa-repeat");
  } catch (error) {
    el.classList.remove("fa-spinner");
    el.classList.add("fa-repeat");
    console.error(error);
  }
}

async function deleteQueueItem(container, el) {
  el.classList.remove("fa-repeat");
  el.classList.add("fa-spinner");

  const id = el.dataset.id;
  const csrfToken = getCookie("csrftoken");
  const url = "/api/delete-queue-item";
  try {
    const response = await fetch(url, {
      method: "POST",
      body: JSON.stringify({ id: id }),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error);
    }

    var row = container.querySelector("#item" + id);
    row.parentNode.removeChild(row);
  } catch (error) {
    el.classList.remove("fa-spinner");
    el.classList.add("fa-repeat");
    console.error(error);
  }
}
