from dataclasses import dataclass
from .driver import BaseDriverData, BaseDriver, Episodes


@dataclass
class SimpleManga:
    driver: BaseDriver
    id: str
    title: str
    thumbnail: str
    author: list
    latest: str
    is_end: bool

    @property
    def details(self):
        return self.driver.get_details(self.id)

    @property
    def dict(self):
        return {
            "driver": self.driver.identifier,
            "id": self.id,
            "title": self.title,
            "thumbnail": self.thumbnail,
            "latest": self.latest,
            "isEnd": self.is_end,
            "author": self.author,
        }


@dataclass
class Manga:
    categories_list = [
        "Passionate",
        "Love",
        "Campus",
        "Yuri",
        "BL",
        "Adventure",
        "Harem",
        "Sci-Fi",
        "War",
        "Suspense",
        "Speculation",
        "Funny",
        "Fantasy",
        "Magic",
        "Horror",
        "Ghosts",
        "History",
        "Fan-Fi",
        "Sports",
        "Hentai",
        "Mecha",
        "Restricted",
        "Cross-Dressing",
    ]

    driver: str
    id: str
    thumbnail: str
    title: str
    author: str
    description: str
    is_end: bool
    categories: tuple
    episodes: Episodes
    driver: BaseDriver
    driver_data: BaseDriverData

    @property
    def dict(self):
        return {
            "driver": self.driver.identifier,
            "id": self.id,
            "title": self.title,
            "thumbnail": self.thumbnail,
            "isEnd": self.is_end,
            "author": self.author,
            "categories": self.categories,
            "episodes": self.episodes.dict,
            "description": self.description,
            "driverData": self.driver_data.compressed,
        }

    @property
    def to_simple(self):
        return SimpleManga(
            driver=self.driver,
            id=self.id,
            title=self.title,
            thumbnail=self.thumbnail,
            is_end=self.is_end,
            latest=self.episodes.serial[0] if len(self.episodes.serial) else None,
            author=self.author,
        )

    @property
    def simple_dict(self):
        return self.to_simple.dict

    def get_episode(self, episode: int, is_extra: bool = False):
        return self.driver.get_episode(episode, is_extra, self.driver_data)
