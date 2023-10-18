from main.views import BetterMangaApp
from django.conf import settings


class serverInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers = {
            **response.headers,
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Expose-Headers": "Version, Available-Drivers",
            "Version": settings.VERSION,
            "Available-Drivers": ",".join(
                map(lambda x: x.identifier, BetterMangaApp.available_drivers),
            ),
        }

        return response
