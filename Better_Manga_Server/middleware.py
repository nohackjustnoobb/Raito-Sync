from main.views import BetterMangaApp


class serverInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        app_details = BetterMangaApp.get_app_details()
        response.headers = {
            **response.headers,
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Expose-Headers": ", ".join(app_details.keys()),
            **app_details,
        }

        return response
