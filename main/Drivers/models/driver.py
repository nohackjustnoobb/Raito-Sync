class BaseDriver:
    identifier = ""
    supported_categories = []
    support_suggestion = False
    recommended_chunk_size = 0
    proxy_settings = {}

    @staticmethod
    def get_details(ids: list, show_all: bool) -> list:
        pass

    @staticmethod
    def search(text: str, page: int) -> list:
        pass

    @staticmethod
    def get_chapter(id: str, extra_data: str) -> list:
        pass

    @staticmethod
    def get_list(category: str, page: int) -> list:
        pass

    @staticmethod
    def check_online() -> bool:
        pass
