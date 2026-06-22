export function init(container) {
  initializeIssuesTable(container);
  bindEvents(container);
}

export function destroy(container) {
  container.removeEventListener("click", handleClick);
}

function bindEvents(container) {
  container.addEventListener("click", handleClick);
}

function handleClick(e) {
  const searchItem = e.target.closest("#searchAllMissing");
  const deleteItem = e.target.closest("#deleteComic");
  const downloadItem = e.target.closest("#downloadIssue");
  if (searchItem) {
    searchAllMissing(e.currentTarget);
  } else if (deleteItem) {
    deleteComic(e.currentTarget);
  } else if (downloadItem) {
    downloadIssue(e.currentTarget, downloadItem);
  }
}

async function downloadIssue(container, el) {
  const id = el.dataset.id;
  el.classList.remove("fa-download");
  el.classList.add("fa-spinner");

  const csrfToken = getCookie("csrftoken");
  const url = "/api/download-issue";
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
    el.classList.add("fa-cloud-download");
  } catch (error) {
    el.classList.remove("fa-spinner");
    el.classList.add("fa-download");
    console.error(error);
  }
}

async function searchAllMissing(container) {
  let el = container.querySelector("#searchAllMissing");
  const id = el.dataset.id;

  const csrfToken = getCookie("csrftoken");
  const url = "/api/search-all-missing";
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
  } catch (error) {
    console.error(error);
  }
}

async function deleteComic(container) {
  let result = await confirm(
    "Are you sure to delete this comic? All data will be deleted, but not files.",
  );
  if (result) {
    let el = container.querySelector("#deleteComic");
    const id = el.dataset.id;

    const csrfToken = getCookie("csrftoken");
    const url = "/api/comic";
    try {
      const response = await fetch(url, {
        method: "DELETE",
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
      document.location.href = "/";
    } catch (error) {
      console.error(error);
    }
  }
}

function initializeIssuesTable(container) {
  const el = container.querySelector("#comic-detail-issues-wrapper");
  if (!el) return;

  // prevent double render
  if (el.dataset.initialized === "1") return;
  el.dataset.initialized = "1";
  let comic_id = el.dataset.comicId;

  new gridjs.Grid({
    columns: [
      "#",
      "Title",
      "Year",
      "Volume",
      "Issue",
      {
        name: "Size",
        sort: false,
        formatter: (cell) =>
          cell
            ? cell
            : gridjs.html(
                `<i title="Issue missing from disk" class="fa fa-exclamation-triangle"></i>`,
              ),
      },
      {
        name: "Actions",
        sort: false,
        formatter: (cell, row) => {
          let html = `<div class="actions-container">`;

          if (cell.filesize === 0) {
            if (cell.queue) {
              html += `<i title="Status: ${cell.queue.status}&#013;Priority: ${cell.queue.priority}"
                           class="fa fa-cloud-download download ${cell.id}"></i>`;
            } else {
              html += `<i title="Download issue"
                           id="downloadIssue"
                           class="fa fa-download download ${cell.id}}"
                           data-id="${cell.id}"></i>`;
            }
          } else {
            html += `<a href="${cell.file_url}"><i title="Download Issue To Device" class="fa fa-arrow-circle-down"></i></a>`;
          }

          if (cell.source === "readallcomics") {
            html += `
                <a href="${cell.remote_id}" target="_blank">
                  <i title="Open remote link" class="fa fa-external-link"></i>
                </a>
              `;
          }
          html += "</div>";

          return gridjs.html(html);
        },
      },
    ],
    server: {
      url: `/api/comic/${comic_id}/issues?`,
      then: (data) =>
        data.results.map((issue) => [
          issue.priority,
          issue.original_text,
          issue.year,
          issue.volume,
          issue.issue,
          issue.filesize,
          issue,
        ]),
      total: (data) => data.count,
    },
    search: {
      server: {
        url: (prev, keyword) => `${prev}&search=${keyword}`,
      },
    },
    pagination: {
      limit: 100,
      server: {
        url: (prev, page, limit) =>
          `${prev}&limit=${limit}&offset=${page * limit}`,
      },
    },
    sort: {
      server: {
        url: (prev, columns) => {
          if (!columns.length) return prev;

          const col = columns[0];
          const dir = col.direction === 1 ? "-" : "";
          let colName = [
            "priority",
            "original_text",
            "year",
            "volume",
            "issue",
          ][col.index];

          return `${prev}&ordering=${dir}${colName}`;
        },
      },
    },
    className: {
      td: "td",
      table: "table",
      th: "th",
      tr: "tr",
      search: "search",
      footer: "footer",
      pagination: "pagination",
      paginationButton: "pagination-button",
    },
  }).render(container.querySelector("#comic-detail-issues-wrapper"));
}
