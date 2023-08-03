from dataclasses import dataclass
from .driver import BaseDriverData, BaseDriver, Chapters


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
        "SciFi",
        "War",
        "Suspense",
        "Speculation",
        "Funny",
        "Fantasy",
        "Magic",
        "Horror",
        "Ghosts",
        "History",
        "FanFi",
        "Sports",
        "Hentai",
        "Mecha",
        "Restricted",
        "CrossDressing",
    ]

    driver: str
    id: str
    thumbnail: str
    title: str
    author: str
    description: str
    is_end: bool
    categories: tuple
    chapters: Chapters
    driver: BaseDriver
    driver_data: BaseDriverData
    latest: str = None

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
            "chapters": self.chapters.dict,
            "description": self.description,
            "driverData": self.driver_data.compressed,
            "latest": self.latest,
        }

    @property
    def to_simple(self):
        return SimpleManga(
            driver=self.driver,
            id=self.id,
            title=self.title,
            thumbnail=self.thumbnail,
            is_end=self.is_end,
            latest=self.latest
            if self.latest
            else self.chapters.serial[0]
            if len(self.chapters.serial)
            else self.chapters.extra[0]
            if len(self.chapters.extra)
            else None,
            author=self.author,
        )

    @property
    def simple_dict(self):
        return self.to_simple.dict

    def get_chapter(self, chapter: int, is_extra: bool = False):
        return self.driver.get_chapter(chapter, is_extra, self.driver_data)
