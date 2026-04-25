from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.cache import cache
from cloudscraper import CloudScraper
import cloudscraper
from bs4 import BeautifulSoup as BS
from pprint import pprint


# cs = CloudScraper()
cs = cloudscraper.create_scraper(
    interpreter='js2py',  # Recommended for v3 challenges
    delay=5,              # Allow more time for complex challenges
    debug=True  
)

READALLCOMICS_URL = "https://readallcomics.com"
READALLCOMICS_SEARCH_URL = "https://readallcomics.com/?story={query}&s=&type=comic"

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


@api_view(["GET"])
def search_remote(request):
    query = request.GET.get("query")

    # if exists return from cache
    if cache.get(f"search-data-{query}"):
        return Response(cache.get(f"search-data-{query}"))
   

    try:
        res = cs.get(READALLCOMICS_SEARCH_URL.format(query=query))
        if res.status_code != 200:
            return Response({"error": "Couldn't fetch data from readallcomics"}, status=status.HTTP_400_BAD_REQUEST)
        soup = BS(res.content, "html.parser")
    except Error as e:
        return Response({"error": f"Unknown error: {e}"})

    ul = soup.find('ul', {'class': 'list-story'})
    items = ul.find_all('li')

    result = []

    for item in items:
        cover = item.find("img")
        if cover:
            cover = cover["src"]

        name = item.find('a', {"class": 'cat-title'})
        if name:
            name = name.text.strip()
        else:
            name = "No Title"

        publisher = item.find('div', {'class': 'cat-publisher'})
        if publisher:
            publisher = publisher.text.replace("Publisher: ", "").strip()
        else:
            publisher = "No data"

        genres = item.find('div', {'class': 'cat-genres'})
        if genres:
            genres = genres.text.replace("Genres: ", "").strip().split(', ')
        else:
            genres = ["No data"]

        year = item.find('div', {'class': 'cat-total-issues'})
        if year:
            year = year.text.split('-')[0].replace("Year:", "").strip()
        else:
            year = "No data"

        total_issues = item.find('div', {'class': 'cat-total-issues'})
        if total_issues:
            total_issues = total_issues.text.split('-')[-1].replace("Issues", "").strip()

        result.append({
            "cover": cover,
            "name": name,
            "publisher": publisher,
            "genres": genres,
            "year": year,
            "total_issues": total_issues
        })

    # cache before returning
    cache.set(f'search-data-{query}', result, 60 * 60)

    return Response(comics)

