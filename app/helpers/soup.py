from bs4 import BeautifulSoup as BS
import re
from app.types import RemoteComic

YEAR_REGEX = r"\d{4}"
TOTAL_ISSUES_REGEX = r"\d+"


def parse_comics_from_response(html: str = "") -> list[RemoteComic]:
    if not html:
        return []

    try:
        soup = BS(html, "html.parser")
    except Exception as e:
        print("[ Error parsing html ]", e)
        return []

    ul = soup.find("ul", {"class": "list-story"})
    if not ul:
        return []

    items = ul.find_all("li")  # type: ignore

    result = []

    for item in items:
        cover = item.find("img")
        if cover:
            cover = str(cover["src"])
        else:
            cover = None

        name_element = item.find("a", {"class": "cat-title"})
        if name_element:
            url = str(name_element["href"])
            name = name_element.text.strip()
        else:
            # No name and url, pass
            continue

        publisher = item.find("div", {"class": "cat-publisher"})
        if publisher:
            publisher = publisher.text.replace("Publisher: ", "").strip()
        else:
            publisher = None

        genres = item.find("div", {"class": "cat-genres"})
        if genres:
            genres = genres.text.replace("Genres: ", "").strip().split(", ")
        else:
            genres = []

        year = item.find("div", {"class": "cat-total-issues"})
        if year:
            year = year.text.split("-")[0]
            match = re.search(YEAR_REGEX, year)
            year = int(match.group()) if match else None
        else:
            year = None

        total_issues = item.find("div", {"class": "cat-total-issues"})
        if total_issues and len(total_issues.text.split("-")) > 1:
            total_issues = total_issues.text.split("-")[1]
            match = re.search(TOTAL_ISSUES_REGEX, total_issues)
            total_issues = int(match.group()) if match else None
        else:
            total_issues = None

        comic = RemoteComic(
            name=name,
            url=url,
            cover=cover,
            publisher=publisher,
            genres=genres,
            year=year,
            total_issues=total_issues,
        )

        result.append(comic)

    return result
