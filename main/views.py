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
            try:
                parameters = request.query_params
                driver = parameters["driver"]
                category = parameters.get("category")
                page = parameters.get("page")
                if page:
                    page = int(page)
            except:
                return Response(
                    {"error": '"driver" is missing.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = BetterMangaApp.get_list(driver, category, page)
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(
                {"error": "An unexpected error occurred when trying to get list."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Suggestion(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request, format=None):
        try:
            try:
                parameters = request.query_params
                driver = parameters["driver"]
                keyword = parameters["keyword"]
            except:
                return Response(
                    {"error": '"driver" or "keyword" are missing.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = BetterMangaApp.get_suggestion(driver, keyword)
            return Response(response, status=status.HTTP_200_OK)

        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(
                {
                    "error": "An unexpected error occurred when trying to get suggestions."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class Drivers(APIView):
    def get(self, request, format=None):
        try:
            try:
                driver = request.query_params["driver"]
            except:
                Response(
                    {"error": '"driver" is missing.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = BetterMangaApp.get_info(driver)
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(
                {"error": "An unexpected error occurred when trying to get driver."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Details(APIView):
    def get(self, request, format=None):
        try:
            try:
                parameters = request.query_params
                driver = parameters["driver"]
                ids = parameters["ids"].split(",")
                show_all = bool(int(parameters.get("show-all", "0")))
            except:
                return Response(
                    {"error": '"driver" or "ids" are missing.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = BetterMangaApp.get_details(driver, ids, show_all)
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(
                {"error": "An unexpected error occurred when trying to get details."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Search(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request, format=None):
        try:
            try:
                parameters = request.query_params
                driver = parameters["driver"]
                keyword = parameters["keyword"]
                page = int(parameters.get("page", "1"))
            except:
                return Response(
                    {"error": '"driver" or "keyword" are missing.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = BetterMangaApp.search(driver, keyword, page)
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(
                {"error": "An unexpected error occurred when trying to search manga."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Chapter(APIView):
    def post(self, request, format=None):
        try:
            try:
                parameters = request.query_params
                driver = parameters["driver"]
                chapter = int(parameters["chapter"])
                is_extra = bool(int(parameters.get("is-extra", "0")))
            except:
                return Response(
                    {"error": '"driver" or "chapter" are missing.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = BetterMangaApp.get_chapter(
                driver, chapter, is_extra, request.data
            )
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(
                {
                    "error": "An error occurred when trying to get chapters. Check if you included the manga data in the body."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
