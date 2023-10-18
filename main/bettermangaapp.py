from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from .Drivers.dm5_driver import DM5
from .Drivers.mhg_driver import MHG
from .Drivers.mhr_driver import MHR
from .Drivers.util import use_proxy


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
        result = (
            list(map(lambda x: x.dict, driver.search(text, page))) if driver else []
        )
        if proxy:
            for i in result:
                i["thumbnail"] = use_proxy(
                    driver.identifier, i["thumbnail"], "thumbnail"
                )

        return result

    @staticmethod
    def get_list(driver_id: str, category: str, page: int, proxy: bool):
        driver = BetterMangaApp.get_driver(id=driver_id)
        if not driver:
            raise DriverNotFound

        result = (
            list(map(lambda x: x.dict, driver.get_list(category, page)))
            if driver
            else []
        )

        if proxy:
            for i in result:
                i["thumbnail"] = use_proxy(
                    driver.identifier, i["thumbnail"], "thumbnail"
                )

        return result

    @staticmethod
    def get_details(driver_id: str, ids: list, show_all: bool, proxy: bool):
        driver = BetterMangaApp.get_driver(id=driver_id)
        if not driver:
            raise DriverNotFound

        result = list(
            map(
                lambda x: x.dict,
                driver.get_details(ids, show_all),
            )
        )

        if proxy:
            for i in result:
                i["thumbnail"] = use_proxy(
                    driver.identifier, i["thumbnail"], "thumbnail"
                )

        return result

    @staticmethod
    def get_chapter(driver_id: str, id: str, extra_data: str, proxy: bool):
        driver = BetterMangaApp.get_driver(id=driver_id)
        if not driver:
            raise DriverNotFound

        result = driver.get_chapter(id, extra_data)

        if proxy:
            result = list(
                map(lambda x: use_proxy(driver.identifier, x, "manga"), result)
            )

        return result

    @staticmethod
    def get_suggestion(driver_id: str, text: str):
        driver = BetterMangaApp.get_driver(id=driver_id)
        if not driver:
            raise DriverNotFound
        return driver.get_suggestion(text)

    @staticmethod
    def get_info(driver_id: str):
        driver = BetterMangaApp.get_driver(id=driver_id)
        if not driver:
            raise DriverNotFound
        return {
            "supportedCategories": driver.supported_categories,
            "recommendedChunkSize": driver.recommended_chunk_size,
        }

    @staticmethod
    def get_proxy(ids: list = []):
        result = {}

        for i in (
            ids
            if len(ids) != 0
            else map(lambda x: x.identifier, BetterMangaApp.available_drivers)
        ):
            driver = BetterMangaApp.get_driver(id=i)
            if driver:
                result[driver.identifier] = driver.proxy_settings

        return result

    @staticmethod
    def check_online(ids: list = []):
        result = {}

        def check_driver_online(id):
            driver = BetterMangaApp.get_driver(id=id)

            if driver:
                start = datetime.now()
                is_online = driver.check_online()
                result[driver.identifier] = {
                    "online": is_online,
                    "latency": (datetime.now() - start).microseconds / 1000
                    if is_online
                    else 0,
                }

        with ThreadPoolExecutor(max_workers=10) as pool:
            pool.map(
                check_driver_online,
                ids
                if len(ids) != 0
                else map(lambda x: x.identifier, BetterMangaApp.available_drivers),
            )

        return result
