from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.cache import cache

from app import sources # type: ignore


@api_view(["GET"])
def get_discover_data(request):
    source = request.GET.get("source", sources.default)

    cache_key = f"discover-data-{source}"
    # if exists return from cache
    if cache.get(cache_key):
        return Response(cache.get(cache_key))

    try:
        source_instance = getattr(sources, source)
    except Exception:
        return Response({"error": "Unknown source"}, status=status.HTTP_400_BAD_REQUEST)

    result, error = source_instance.discover()

    if error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    result_json = []
    for item in result:
        result_json.append(item.serialize())

    # cache before returning
    cache.set(cache_key, result_json, 60 * 60)

    return Response(result_json)


@api_view(["GET"])
def search_remote(request):
    query = request.GET.get("query")
    source = request.GET.get("source", sources.default)

    cache_key = f"search-data-{query.replace(' ', '-')}-{source}"
    # if exists return from cache
    if cache.get(cache_key):
        return Response(cache.get(cache_key))

    try:
        source_instance = getattr(sources, source)
    except Exception:
        return Response({"error": "Source not found"}, status=status.HTTP_400_BAD_REQUEST)

    result, error = source_instance.search(query)

    if error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    result_json = []
    for item in result:
        result_json.append(item.serialize())

    # cache before returning
    cache.set(cache_key, result_json, 60 * 60)

    return Response(result_json)
