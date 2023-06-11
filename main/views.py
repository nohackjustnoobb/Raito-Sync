from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .Drivers.dm5_driver import DM5
from .Drivers.mhg_driver import MHG


cache_time = 5 * 60


class BetterMangaApp:
    version = "Development"
    available_drivers = [DM5, MHG]

    @staticmethod
    def get_driver(id: str):
        for i in BetterMangaApp.available_drivers:
            if i.identifier == id:
                return i
        return None

    @staticmethod
    def search(driver_id: str, text: str, page: int):
        driver = BetterMangaApp.get_driver(id=driver_id)
        result = driver.search(text, page)
        return list(map(lambda x: x.dict, result)) if driver else []

    @staticmethod
    def get_list(driver_id: str, category: str, page: int):
        driver = BetterMangaApp.get_driver(id=driver_id)
        return (
            list(map(lambda x: x.dict, driver.get_list(category, page)))
            if driver
            else []
        )

    @staticmethod
    def get_details(driver_id: str, ids: list, show_all: bool):
        driver = BetterMangaApp.get_driver(id=driver_id)
        return (
            list(
                map(
                    lambda x: x.dict if show_all else x.simple_dict,
                    driver.get_details(ids),
                )
            )
            if driver
            else []
        )

    @staticmethod
    def get_episode(driver: str, episode: int, is_extra: bool, data: str):
        return driver.get_episode(episode, is_extra, data) if driver else None

    @staticmethod
    def get_suggestion(driver_id: str, text: str):
        driver = BetterMangaApp.get_driver(id=driver_id)
        return (
            driver.get_suggestion(text) if driver and driver.support_suggestion else []
        )

    @staticmethod
    def get_app_details():
        return {
            "Version": BetterMangaApp.version,
            "Available-Drivers": ", ".join(
                map(lambda x: x.identifier, BetterMangaApp.available_drivers),
            ),
        }

    @staticmethod
    def get_categories(driver_id: str):
        driver = BetterMangaApp.get_driver(id=driver_id)
        return (
            {
                "categories": driver.supported_categories,
                "suggestion": driver.support_suggestion,
            }
            if driver
            else None
        )


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
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Suggestion(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request, format=None):
        try:
            parameters = request.query_params
            response = BetterMangaApp.get_suggestion(parameters["d"], parameters["k"])
            return Response(response, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Categories(APIView):
    def get(self, request, format=None):
        try:
            parameters = request.query_params
            response = BetterMangaApp.get_categories(parameters["d"])
            return Response(response, status=status.HTTP_200_OK)
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
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
