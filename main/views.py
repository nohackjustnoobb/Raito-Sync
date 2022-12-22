from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .Drivers.dm5_driver import DM5
from .Drivers.mhg_driver import MHG


cache_time = 5 * 60


class BetterMangaApp:
    version = "Beta"
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
    def get_recommendation(driver_id: str, text: str):
        driver = BetterMangaApp.get_driver(id=driver_id)
        return (
            driver.get_recommendation(text)
            if driver and driver.support_recommendation
            else []
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
                "recommendation": driver.support_recommendation,
            }
            if driver
            else None
        )


def get_response(status, body=None):
    app_details = BetterMangaApp.get_app_details()
    return Response(
        body,
        status=status,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Expose-Headers": ", ".join(app_details.keys()),
            **app_details,
        },
    )


class List(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request, format=None):
        try:
            parameters = request.query_params
            response = BetterMangaApp.get_list(
                parameters["driver"],
                parameters["category"] if parameters.get("category") else None,
                int(parameters["page"]) if parameters.get("page") else None,
            )
            return get_response(status.HTTP_200_OK, response)
        except:
            return get_response(status.HTTP_400_BAD_REQUEST)


class Recommendation(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request, format=None):
        try:
            parameters = request.query_params
            response = BetterMangaApp.get_recommendation(
                parameters["driver"], parameters["text"]
            )
            return get_response(status.HTTP_200_OK, response)
        except:
            return get_response(status.HTTP_400_BAD_REQUEST)


class Categories(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request, format=None):
        try:
            parameters = request.query_params
            response = BetterMangaApp.get_categories(parameters["driver"])
            return get_response(status.HTTP_200_OK, response)
        except:
            return get_response(status.HTTP_400_BAD_REQUEST)


class Details(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request, format=None):
        try:
            parameters = request.query_params
            ids = parameters["ids"].split(",")
            response = BetterMangaApp.get_details(
                parameters["driver"],
                ids,
                int(parameters["show_all"]) == 1
                if parameters.get("show_all")
                else False,
            )
            return get_response(status.HTTP_200_OK, response)
        except:
            return get_response(status.HTTP_400_BAD_REQUEST)


class Search(APIView):
    @method_decorator(cache_page(cache_time))
    def get(self, request, format=None):
        try:
            parameters = request.query_params
            response = BetterMangaApp.search(
                parameters["driver"],
                parameters["text"],
                int(parameters["page"]) if parameters.get("page") else 1,
            )
            return get_response(status.HTTP_200_OK, response)
        except:
            return get_response(status.HTTP_400_BAD_REQUEST)


class Episode(APIView):
    def post(self, request, format=None):
        try:
            parameters = request.query_params
            driver = BetterMangaApp.get_driver(id=parameters["driver"])
            response = BetterMangaApp.get_episode(
                driver,
                int(parameters["episode"]),
                parameters["is_extra"] if parameters.get("is_extra") else 0,
                request.data,
            )
            return get_response(status.HTTP_200_OK, response)
        except:
            return get_response(status.HTTP_400_BAD_REQUEST)
