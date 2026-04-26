from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.cache import cache
import cloudscraper

from app.helpers.soup import parse_comics_from_response

# cs = CloudScraper()
cs = cloudscraper.create_scraper(
    interpreter="js2py",  # Recommended for v3 challenges
    delay=5,  # Allow more time for complex challenges
    debug=True,
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
            return Response(
                {"error": "Couldn't fetch from readallcomics.com"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    result = parse_comics_from_response(str(res.content))

    result_json = []
    for item in result:
        result_json.append(item.serialize())

    # cache before returning
    cache.set("discover-data", result_json, 60 * 60)

    return Response(result_json)


@api_view(["GET"])
def search_remote(request):
    query = request.GET.get("query")

    # if exists return from cache
    if cache.get(f"search-data-{query}"):
        return Response(cache.get(f"search-data-{query}"))

    try:
        res = cs.get(READALLCOMICS_SEARCH_URL.format(query=query))
        if res.status_code != 200:
            return Response(
                {"error": "Couldn't fetch data from readallcomics"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        return Response({"error": f"Unknown error: {e}"})

    result = parse_comics_from_response(str(res.content))

    result_json = []
    for item in result:
        result_json.append(item.serialize())

    # cache before returning
    cache.set(f"search-data-{query}", result_json, 60 * 60)

    return Response(result_json)
