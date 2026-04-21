from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.cache import cache
from cloudscraper import CloudScraper
from bs4 import BeautifulSoup as BS
from pprint import pprint


cs = CloudScraper()
READALLCOMICS_URL = "https://readallcomics.com"

@api_view(["GET"])
def get_discover_data(request):
    # if exists return from cache
    if cache.get("discover-data"):
        return Response(cache.get("discover-data"))

    try:
        res = cs.get(READALLCOMICS_URL)
        if res.status_code != 200:
            return Response({"error": "Couldn't fetch from readallcomics.com"}, status=status.HTTP_400_BAD_REQUEST)
        soup = BS(res.content, "html.parser")
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    ul = soup.find('ul', {'class': 'list-story'})
    items = ul.find_all('li')

    comics = []

    for item in items:
        cover = item.find("img")
        if cover:
            cover = cover["src"]
        name = item.find('a', {"class": 'cat-title'}).text.strip()
        publisher = item.find('div', {'class': 'cat-publisher'}).text.replace("Publisher: ", "").strip()
        genres = item.find('div', {'class': 'cat-genres'}).text.replace("Genres: ", "").strip().split(', ')
        year = item.find('div', {'class': 'cat-total-issues'}).text.split('-')[0].replace("Year:", "").strip()
        total_issues = item.find('div', {'class': 'cat-total-issues'}).text.split('-')[-1].replace("Issues", "").strip()
        comics.append({
            "cover": cover,
            "name": name,
            "publisher": publisher,
            "genres": genres,
            "year": year,
            "total_issues": total_issues
        })

    # cache before returning
    cache.set('discover-data', comics, 60 * 60)

    return Response(comics)

