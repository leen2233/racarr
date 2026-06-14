  document.addEventListener("DOMContentLoaded", initializeIssuesTable);
  document.addEventListener("content:loaded", initializeIssuesTable);

  async function downloadIssue(id) {
    var icon = document.getElementById(id);
    icon.classList.remove("fa-download");
    icon.classList.add("fa-spinner");

    const csrfToken = getCookie("csrftoken")
    const url = "/api/download-issue";
    try {
      const response = await fetch(url, {
        method: "POST", 
        body: JSON.stringify({id: id}),
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        }
      });
      
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error);
      }

      icon.classList.remove("fa-spinner");
      icon.classList.add("fa-cloud-download");
    } catch (error){
      icon.classList.remove("fa-spinner");
      icon.classList.add("fa-download");
      console.error(error);
    }
  }

  async function searchAllMissing(id) {
    const csrfToken = getCookie("csrftoken")    
    const url = "/api/search-all-missing"
    try {
      const response = await fetch(url, {
        method: "POST",
        body: JSON.stringify({id: id}),
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken
        }
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error(error)
    }
  }

  async function deleteComic(id) {
    let result = await confirm("Are you sure to delete this comic? All data will be deleted, but not files.")
    if (result) {
      const csrfToken = getCookie("csrftoken")    
      const url = "/api/comic"
      try {
        const response = await fetch(url, {
          method: "DELETE",
          body: JSON.stringify({id: id}),
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
          }
        });

        const result = await response.json();
        if (!response.ok) {
          throw new Error(result.error);
        }    
        document.location.href = "/";
      } catch (error) {
        console.error(error)
      }
   
    }
  }

  function initializeIssuesTable() { 
    const el = document.getElementById("comic-detail-issues-wrapper");
    if (!el) return;

    // prevent double render
    if (el.dataset.initialized === "1") return;
    el.dataset.initialized = "1";
    let comic_id = el.dataset.comicId

    new gridjs.Grid({
      columns: [
        "#", "Title", "Year", "Volume", "Issue", { 
          name: 'Size',
          sort: false,
          formatter: (cell) => cell ? cell : gridjs.html(`<i title="Issue missing from disk" class="fa fa-exclamation-triangle"></i>`)
        },
        {
          name: "Actions",
          sort: false,
          formatter: (cell, row) => {
            let html = `<div class="actions-container">`;

            if (cell.filesize === 0) {
              if (cell.queue) {
                html += `<i title="Status: ${cell.queue.status}&#013;Priority: ${cell.queue.priority}"
                           id="${cell.id}"
                           class="fa fa-cloud-download download"></i>`;
              } else {
                html += `<i title="Download issue"
                           id="${cell.id}"
                           class="fa fa-download download"
                           onClick="downloadIssue(${cell.id})"></i>`;
              }
            }

            if (cell.source === "readallcomics") {
              html += `
                <a href="${cell.remote_id}" target="_blank">
                  <i title="Open remote link" class="fa fa-external-link"></i>
                </a>
              `;
            }
            html += "</div>"

            return gridjs.html(html);
          }
        },
      ],
      server: {
        url: `/api/comic/${comic_id}/issues?`,
        then: data => data.results.map(issue => 
          [issue.priority, issue.original_text, issue.year, issue.volume, issue.issue, issue.filesize, issue]
        ),
        total: data => data.count
      },
      search: {
        server: {
          url: (prev, keyword) => `${prev}&search=${keyword}`
        }
      },
      pagination: {
        limit: 100,
        server: {
          url: (prev, page, limit) => `${prev}&limit=${limit}&offset=${page * limit}`
        }
      },
      sort: {
        server: {
          url: (prev, columns) => {
            if (!columns.length) return prev;
            
            const col = columns[0];
            const dir = col.direction === 1 ? '-' : '';
            let colName = ['priority', 'original_text', 'year', 'volume', 'issue'][col.index];
            
            return `${prev}&ordering=${dir}${colName}`;
         }
        }
      },
      className: {
        td: 'td',
        table: 'table',
        th: 'th',
        tr: 'tr',
        search: 'search',
        footer: 'footer',
        pagination: 'pagination',
        paginationButton: 'pagination-button'
      }
    }).render(document.getElementById("comic-detail-issues-wrapper"));

  }

