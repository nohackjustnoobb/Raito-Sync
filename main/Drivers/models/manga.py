from dataclasses import dataclass
from .driver import BaseDriver


@dataclass
class Chapter:
    title: str
    id: str

    @property
    def dict(self):
        return {"title": self.title, "id": self.id}


@dataclass
class Chapters:
    serial: list[Chapter]
    extra: list[Chapter]
    extra_data: str

    @property
    def dict(self):
        return {
            "serial": [i.dict for i in self.serial],
            "extra": [i.dict for i in self.extra],
            "extraData": self.extra_data,
        }


@dataclass
class SimpleManga:
    driver: BaseDriver
    id: str
    title: str
    thumbnail: str
    latest: str
    is_end: bool

    @property
    def details(self):
        return self.driver.get_manga(self.id)

    @property
    def dict(self):
        return {
            "driver": self.driver.identifier,
            "id": self.id,
            "title": self.title,
            "thumbnail": self.thumbnail,
            "latest": self.latest,
            "isEnd": self.is_end,
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
    id: str
    thumbnail: str
    title: str
    author: str
    description: str
    is_end: bool
    author: list
    categories: tuple
    chapters: Chapters
    driver: BaseDriver
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
            else self.chapters.serial[0].title
            if len(self.chapters.serial)
            else self.chapters.extra[0].title
            if len(self.chapters.extra)
            else None,
        )

    @property
    def simple_dict(self):
        return self.to_simple.dict

    def get_chapter(self, chapter: int, is_extra: bool = False):
        return self.driver.get_chapter(chapter, is_extra, self.driver_data)
