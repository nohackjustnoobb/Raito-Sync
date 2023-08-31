from dataclasses import dataclass
import json
import base64
import lzma


@dataclass
class Chapters:
    serial: list
    extra: list

    @property
    def dict(self):
        return {
            "serial": self.serial,
            "extra": self.extra,
        }


@dataclass
class BaseDriverData:
    @property
    def dict(self):
        pass

    @staticmethod
    def from_dict(dict: dict):
        pass

    @staticmethod
    def from_compressed(compressed: str):
        pass

    @staticmethod
    def _from_compresssed(driverData, compressed):
        return driverData.from_dict(json.loads(BaseDriverData.decompress(compressed)))

    @property
    def compressed(self):
        text = json.dumps(self.dict)
        compressed = base64.b64encode(lzma.compress(text.encode())).decode()
        return compressed

    @staticmethod
    def decompress(compressed: str):
        return lzma.decompress(base64.b64decode(compressed)).decode()


class BaseDriver:
    identifier = ""
    supported_categories = []
    support_suggestion = False
    recommended_chunk_size = 0
    proxy_settings = {}

    @staticmethod
    def get_details(ids: list, show_all: bool, proxy: bool) -> list:
        pass

    @staticmethod
    def search(text: str, page: int, proxy: bool) -> list:
        pass

    @staticmethod
    def get_chapter(
        chapter: int, is_extra: bool, data: BaseDriverData, proxy: bool
    ) -> list:
        pass

    @staticmethod
    def get_list(category: str, page: int, proxy: bool) -> list:
        pass

    @staticmethod
    def check_online() -> bool:
        pass
