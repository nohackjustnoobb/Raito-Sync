from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .bettermangaapp import (
    BetterMangaApp,
    DriverNotFound,
)


cache_time = 5 * 60


class Info(APIView):
    def get(self, request):
        return Response(
            {
                "version": settings.VERSION,
                "availableDrivers": map(
                    lambda x: x.identifier, BetterMangaApp.available_drivers
                ),
            },
            status=status.HTTP_200_OK,
        )


class List(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request):
        try:
            try:
                parameters = request.query_params
                driver = parameters["driver"]
                category = parameters.get("category")
                page = parameters.get("page")
                proxy = bool(int(parameters.get("proxy", "0")))
                if page:
                    page = int(page)
            except:
                return Response(
                    {"error": '"driver" is missing.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = BetterMangaApp.get_list(driver, category, page, proxy)
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
    def get(self, request):
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
    def get(self, request):
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


@api_view(["GET", "POST"])
def getManga(request):
    try:
        try:
            parameters = request.query_params
            driver = parameters["driver"]
            ids = (
                request.data["ids"]
                if request.method == "POST"
                else parameters["ids"].split(",")
            )
            show_all = bool(int(parameters.get("show-all", "0")))
            proxy = bool(int(parameters.get("proxy", "0")))
        except:
            return Response(
                {"error": '"driver" or "ids" are missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = BetterMangaApp.get_manga(driver, ids, show_all, proxy)
        return Response(response, status=status.HTTP_200_OK)
    except DriverNotFound:
        return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
    except:
        return Response(
            {"error": "An unexpected error occurred when trying to get manga."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class Search(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request):
        try:
            try:
                parameters = request.query_params
                driver = parameters["driver"]
                keyword = parameters["keyword"]
                page = int(parameters.get("page", "1"))
                proxy = bool(int(parameters.get("proxy", "0")))
            except:
                return Response(
                    {"error": '"driver" or "keyword" are missing.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = BetterMangaApp.search(driver, keyword, page, proxy)
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(
                {"error": "An unexpected error occurred when trying to search manga."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Chapter(APIView):
    def get(self, request):
        try:
            try:
                parameters = request.query_params
                driver = parameters["driver"]
                id = parameters["id"]
                extra_data = parameters.get("extra-data", "")
                proxy = bool(int(parameters.get("proxy", "0")))
            except:
                return Response(
                    {"error": '"driver" or "id" are missing.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = BetterMangaApp.get_chapter(driver, id, extra_data, proxy)
            return Response(response, status=status.HTTP_200_OK)
        except DriverNotFound:
            return Response(DriverNotFound.message, status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(
                {"error": "An error occurred when trying to get chapters."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Proxy(APIView):
    def get(self, request):
        drivers = request.query_params.get("drivers", [])
        if drivers != []:
            drivers = drivers.split(",")

        return Response(BetterMangaApp.get_proxy(drivers), status=status.HTTP_200_OK)


class Online(APIView):
    def get(self, request):
        drivers = request.query_params.get("drivers", [])
        if drivers != []:
            drivers = drivers.split(",")

        return Response(
            BetterMangaApp.check_online(drivers),
            status=status.HTTP_200_OK,
        )
