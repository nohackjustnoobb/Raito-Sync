from .Drivers.dm5_driver import DM5
from .Drivers.mhg_driver import MHG
from .Drivers.mhr_driver import MHR


class DriverNotFound(Exception):
    def message(self):
        return {"error": "Driver not found"}


class BetterMangaApp:
    available_drivers = [MHR, DM5, MHG]

    @staticmethod
    def get_driver(id: str):
        for i in BetterMangaApp.available_drivers:
            if i.identifier == id:
                return i
        return None

    @staticmethod
    def search(driver_id: str, text: str, page: int, proxy: bool):
        driver = BetterMangaApp.get_driver(id=driver_id)
        if not driver:
            raise DriverNotFound
        result = driver.search(text, page, proxy)
        return list(map(lambda x: x.dict, result)) if driver else []

    @staticmethod
    def get_list(driver_id: str, category: str, page: int, proxy: bool):
        driver = BetterMangaApp.get_driver(id=driver_id)
        if not driver:
            raise DriverNotFound
        return (
            list(map(lambda x: x.dict, driver.get_list(category, page, proxy)))
            if driver
            else []
        )

    @staticmethod
    def get_details(driver_id: str, ids: list, show_all: bool, proxy: bool):
        driver = BetterMangaApp.get_driver(id=driver_id)
        if not driver:
            raise DriverNotFound
        return list(
            map(
                lambda x: x.dict,
                driver.get_details(ids, show_all, proxy),
            )
        )

    @staticmethod
    def get_chapter(
        driver_id: str, chapter: int, is_extra: bool, data: str, proxy: bool
    ):
        driver = BetterMangaApp.get_driver(id=driver_id)
        if not driver:
            raise DriverNotFound

        return driver.get_chapter(chapter, is_extra, data, proxy)

    @staticmethod
    def get_suggestion(driver_id: str, text: str):
        driver = BetterMangaApp.get_driver(id=driver_id)
        if not driver:
            raise DriverNotFound
        return driver.get_suggestion(text) if driver.support_suggestion else []

    @staticmethod
    def get_info(driver_id: str):
        driver = BetterMangaApp.get_driver(id=driver_id)
        if not driver:
            raise DriverNotFound
        return {
            "supportedCategories": driver.supported_categories,
            "supportSuggestion": driver.support_suggestion,
            "recommendedChunkSize": driver.recommended_chunk_size,
        }

    @staticmethod
    def get_proxy():
        result = {}
        for i in BetterMangaApp.available_drivers:
            result[i.identifier] = i.proxy_settings

        return result
