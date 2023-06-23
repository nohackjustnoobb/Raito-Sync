from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .bettermangaapp import (
    BetterMangaApp,
    DriverNotFound,
)


cache_time = 5 * 60


class List(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request, format=None):
        try:
            parameters = request.query_params
            response = BetterMangaApp.get_list(
                parameters["d"],
                parameters["c"] if parameters.get("c") else None,
                int(parameters["p"]) if parameters.get("p") else None,
            )
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Suggestion(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request, format=None):
        try:
            parameters = request.query_params
            response = BetterMangaApp.get_suggestion(parameters["d"], parameters["k"])
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Categories(APIView):
    def get(self, request, format=None):
        try:
            parameters = request.query_params
            response = BetterMangaApp.get_categories(parameters["d"])
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Details(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request, format=None):
        try:
            parameters = request.query_params
            ids = parameters["i"].split(",")
            response = BetterMangaApp.get_details(
                parameters["d"],
                ids,
                int(parameters["sa"]) == 1 if parameters.get("sa") else False,
            )
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Search(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request, format=None):
        try:
            parameters = request.query_params
            response = BetterMangaApp.search(
                parameters["d"],
                parameters["k"],
                int(parameters["p"]) if parameters.get("p") else 1,
            )
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Episode(APIView):
    def post(self, request, format=None):
        try:
            parameters = request.query_params
            driver = BetterMangaApp.get_driver(id=parameters["d"])
            response = BetterMangaApp.get_episode(
                driver,
                int(parameters["e"]),
                parameters["ie"] == "1" if parameters.get("ie") else False,
                request.data,
            )
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
