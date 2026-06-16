import os
import random
import re
import string
import zipfile
from typing import Optional, Tuple

from bs4 import BeautifulSoup as BS
from bs4.element import NavigableString, Tag
from django.conf import settings

from app.types import Comic, Issue, SearchItem

from .base import Source

YEAR_REGEX = r"\d{4}"
TOTAL_ISSUES_REGEX = r"\d+"
VOLUME_REGEX = r"\b(?:v|vol)\.?\s*(\d+)"
YEAR_REGEX = r"\(?([1-9]\d{3})\)?"
ANNUAL_REGEX = r"\b(annual|special)\b"


class ReadAllComics(Source):
    NAME = "ReadAllComics"
    BASE_URL = "https://readallcomics.com"

    def search(self, query):
        params = {"story": query, "s": "", "type": "comic"}
        try:
            res = self._make_request("/", params=params)
        except Exception as e:
            return None, str(e)

        result = self._parse_comics_from_response(str(res.content))
        return result

    def discover(self):
        try:
            res = self._make_request("/")
        except Exception as e:
            return None, str(e)

        result = self._parse_comics_from_response(res.content)
        return result

    def get(self, id):
        """
        id: url for comic
        """
        try:
            res = self._make_request(id)
        except Exception as e:
            return None, str(e)

        result = self._parse_comic_from_response(res.content, id)
        return result

    def download(self, id, progress):
        try:
            res = self._make_request(id)
        except Exception as e:
            return None, str(e)

        image_urls, error = self._parse_images_from_response(res.content)
        if error:
            return None, error

        if not image_urls:
            return None, "Couldn't find images from this url"

        # random filename
        output_filename = (
            "".join(random.choice(string.ascii_lowercase) for i in range(20)) + ".cbz"
        )
        output_path = os.path.join(settings.TEMP_DIR, output_filename)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archieve:
            for i, url in enumerate(image_urls, 1):
                try:
                    response = self._make_request(url)
                    response.raise_for_status()
                    img_filename = f"{i:03d}.jpg"
                    archieve.writestr(img_filename, response.content)

                except Exception as e:
                    return (
                        None,
                        "Couldn't download image from url: "
                        + url
                        + ".\n Error:"
                        + str(e),
                    )

                if i % 5 == 0:
                    percentage = int(100 / len(image_urls) * i)
                    progress(percentage)

        # verify cbz file
        with zipfile.ZipFile(output_path, "r") as archieve:
            if len(archieve.namelist()) == 0:
                return None, "No images were successfully downloaded"

        return output_path, None

    def _parse_comics_from_response(
        self, html
    ) -> Tuple[Optional[list[SearchItem]], str]:
        if not html:
            return None, "No html is given"

        try:
            soup = BS(html, "html.parser")
        except Exception as e:
            print("[ HTML PARSE ERROR ]", html)
            return None, f"Error parsing response html: {e}"

        ul = soup.find("ul", {"class": "list-story"})
        if not ul:
            return None, "No comic found in response"

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

            comic = SearchItem(
                name=name,
                id=url,
                cover=cover,
                publisher=publisher,
                genres=genres,
                year=year,
                total_issues=total_issues,
            )

            result.append(comic)

        return result, ""

    def _parse_comic_from_response(self, html, id):
        if not html:
            return None, "No html is given"

        try:
            soup = BS(html, "html.parser")
        except Exception as e:
            print("[ HTML PARSE ERROR ]", html)
            return None, f"Error parsing response html: {e}"

        div = soup.find("div", {"class": "description-archive"})
        if not div:
            return None, "Comic details not found"

        cover = div.find("img")

        if cover:
            cover = str(cover["src"])  # type: ignore
        else:
            cover = None

        name = div.find("h1")
        if name:
            name = name.text.strip()  # type: ignore
        else:
            name = None

        genres = []
        publisher = None
        p = div.find("div", {"class": "b"}).find("p")  # type: ignore
        if p:
            for text in p.text.strip().split("\n"):  # type: ignore
                text = text.strip()
                if text.startswith("Genres:"):
                    genres = text.replace("Genres:", "").strip().split(", ")
                elif text.startswith("Publisher:"):
                    publisher = text.replace("Publisher:", "").strip()

        div = div.find("div", {"class": "b"})  # type: ignore

        description = ""
        for item in div.children:  # type: ignore
            if isinstance(item, Tag):
                if item.name == "span":
                    description += f"<span>{item.text}</span>\n"
            elif isinstance(item, NavigableString):
                text = item.text.strip()
                if text:
                    description += f"<strong>{item.text}</strong>\n"

        issues_div = soup.find("ul", {"class": "list-story"})
        issues = []
        if issues_div:
            # to calculate priority
            issue_count = len(issues_div.find_all("li"))
            counter = 0
            for item in issues_div.find_all("li"):
                link = item.find("a")
                if not link:
                    continue

                print(link)
                url = str(link["href"])
                text = link.text.strip()

                volume_number = self._get_volume_number(text)
                issue_number = self._get_issue_number(text)
                year = self._get_year(text)
                is_annual = self._get_is_annual(text)

                issue = Issue(
                    volume=volume_number,
                    issue=issue_number,
                    original_text=text,
                    year=year,
                    is_annual=is_annual,
                    id=url,
                    name="",
                    priority=issue_count - counter,
                )
                issues.append(issue)
                counter += 1

        comic = Comic(
            name=name,
            id=id,
            description=description,
            cover=cover,
            publisher=publisher,
            genres=genres,
            year=0,
            total_issues=len(issues),
            issues=issues,
        )

        return comic, None

    def _parse_images_from_response(self, html):
        if not html:
            return None, "No html is given"

        try:
            soup = BS(html, "html.parser")
        except Exception as e:
            print("[ HTML PARSE ERROR ]", html)
            return None, f"Error parsing response html: {e}"

        pages = soup.select("center p img")
        urls = []
        for page in pages:
            source = page.get("src")
            if source:
                urls.append(source)

        return urls, None

    def _get_volume_number(self, text: str) -> int:
        match = re.search(VOLUME_REGEX, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 1

    def _get_issue_number(self, text: str) -> Optional[float]:
        # remove year in parentheses to avoid matching it
        text = re.sub(r"\s*[\(\[].*?[\)\]]\s*$", "", text)

        # remove volume part completely (v, vol, part, etc.)
        text = re.sub(r"\b(?:v|vol|part)\.?\s*\d+", "", text, flags=re.IGNORECASE)

        # match issue:
        # prefer #number first, otherwise last standalone number (with optional .1)
        match = re.search(r"#\s*(\d+(?:\.\d+)?)", text)
        if match:
            num = match.group(1)
            return float(num) if "." in num else float(num)

        # get last number in string (avoids picking years or earlier numbers like 94)
        matches = re.findall(r"\b\d+(?:\.\d+)?", text)
        if matches:
            num = matches[-1]
            return float(num) if "." in num else float(num)

        return None

    def _get_year(self, text: str) -> Optional[int]:
        match = re.search(YEAR_REGEX, text)
        if match:
            return int(match.group(1))
        return None

    def _get_is_annual(self, text: str) -> bool:
        return bool(re.search(ANNUAL_REGEX, text, re.IGNORECASE))
