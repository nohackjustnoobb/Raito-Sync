from dataclasses import dataclass
import json
import base64
import lzma
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
import asyncio
import nest_asyncio


@dataclass
class Episodes:
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
    def from_dict(dict):
        pass

    @staticmethod
    def from_compressed(compressed):
        pass

    @staticmethod
    def _from_compresssed(driver, compressed):
        return driver.from_dict(json.loads(BaseDriverData.decompress(compressed)))

    @property
    def compressed(self):
        text = json.dumps(self.dict)
        compressed = base64.b64encode(lzma.compress(text.encode())).decode()
        return compressed

    @staticmethod
    def decompress(compressed):
        return lzma.decompress(base64.b64decode(compressed)).decode()


class BaseDriver:
    identifier = None
    supported_categories = None
    support_suggestion = None

    @staticmethod
    def get_details(ids: list):
        pass

    @staticmethod
    def search(text: str, page: int):
        pass

    @staticmethod
    def get_episode(episode: int, is_extra: bool, data: BaseDriverData):
        pass

    @staticmethod
    def get_list(category: str, page: int):
        pass


nest_asyncio.apply()


def key(_, urls):
    return hashkey(urls)


async def aget(session, urls):
    resp = await session.get(urls)
    return await resp.text()


@cached(cache=TTLCache(maxsize=10, ttl=300), key=key)
def get(session, urls):
    loop = asyncio.get_event_loop()
    coroutine = aget(session, urls)
    return loop.run_until_complete(coroutine)
