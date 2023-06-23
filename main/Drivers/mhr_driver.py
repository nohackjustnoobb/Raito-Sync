from dataclasses import dataclass
import hashlib
import re
import urllib.parse
import requests
import json
import asyncio
import aiohttp
import chinese_converter

from classes.driver import Episodes, BaseDriver, BaseDriverData
from classes.manga import Manga, SimpleManga


@dataclass
class MHRData(BaseDriverData):
    manga_id: str
    episodes_ids: list
    serial_len: int

    def get_episode_ids(self, episode, is_extra):
        return self.episodes_ids[episode + self.serial_len if is_extra else episode]

    @property
    def dict(self):
        return {
            "episodes_urls": self.episodes_ids,
            "serial_len": self.serial_len,
            "manga_id": self.manga_id,
        }

    @staticmethod
    def from_dict(dict):
        return MHRData(
            episodes_ids=dict["episodes_urls"],
            serial_len=dict["serial_len"],
            manga_id=dict["manga_id"],
        )

    @staticmethod
    def from_compressed(compressed):
        return MHRData._from_compresssed(MHRData, compressed)


class MHR(BaseDriver):
    identifier = "MHR"
    categories = {
        31: Manga.categories_list[0],
        26: Manga.categories_list[1],
        1: Manga.categories_list[2],
        3: Manga.categories_list[3],
        27: Manga.categories_list[4],
        2: Manga.categories_list[5],
        8: Manga.categories_list[6],
        25: Manga.categories_list[7],
        12: Manga.categories_list[8],
        17: Manga.categories_list[9],
        33: Manga.categories_list[10],
        37: Manga.categories_list[11],
        14: Manga.categories_list[12],
        15: Manga.categories_list[13],
        29: Manga.categories_list[14],
        20: Manga.categories_list[15],
        4: Manga.categories_list[16],
        30: Manga.categories_list[17],
        34: Manga.categories_list[18],
        36: Manga.categories_list[19],
        40: Manga.categories_list[20],
        61: Manga.categories_list[21],
        5: Manga.categories_list[22],
    }
    categoriesText = {
        "热血": 31,
        "恋爱": 26,
        "校园": 1,
        "百合": 3,
        "彩虹": 27,
        "冒险": 2,
        "后宫": 8,
        "科幻": 25,
        "战争": 12,
        "悬疑": 17,
        "推理": 33,
        "搞笑": 37,
        "奇幻": 14,
        "魔法": 15,
        "恐怖": 29,
        "神鬼": 20,
        "历史": 4,
        "同人": 30,
        "运动": 34,
        "绅士": 36,
        "机甲": 40,
        "限制级": 61,
        "伪娘": 5,
    }
    supported_categories = list(categories.values())
    support_suggestion = True

    @staticmethod
    def hashGETQuery(map):
        def addObj(map, sb, obj):
            sb.append(
                urllib.parse.quote(map[obj], encoding="utf-8")
                .replace("+", "%20")
                .replace("%7E", "~")
                .replace("*", "%2A")
            )

        key = "4e0a48e1c0b54041bce9c8f0e036124d"
        array = sorted(map.keys())

        sb = []
        sb.append(key)
        sb.append("GET")

        for obj in array:
            sb.append(obj)
            try:
                addObj(map, sb, obj)
            except:
                pass

        sb.append(key)

        return hashlib.md5(("".join(sb)).encode()).hexdigest()

    @staticmethod
    def hashPOSTQuery(body, map):
        def addObj(map, sb, obj):
            sb.append(
                urllib.parse.quote(map[obj], encoding="utf-8")
                .replace("+", "%20")
                .replace("%7E", "~")
                .replace("*", "%2A")
            )

        key = "4e0a48e1c0b54041bce9c8f0e036124d"
        map["body"] = json.dumps(body)
        array = sorted(map.keys())

        sb = []
        sb.append(key)
        sb.append("POST")

        for obj in array:
            sb.append(obj)
            try:
                addObj(map, sb, obj)
            except UnicodeEncodeError:
                pass

        sb.append(key)

        hash = hashlib.md5(("".join(sb)).encode()).hexdigest()
        del map["body"]

        return hash

    @staticmethod
    def convert_to_simple(data):
        author = re.split("，| |  ", data["mangaAuthor"])
        author = [s for s in author if s]

        return SimpleManga(
            driver=MHR,
            id=data["mangaId"],
            title=data["mangaName"],
            thumbnail=data["mangaCoverimageUrl"],
            is_end=bool(data["mangaIsOver"]),
            latest=data["mangaNewestContent"]
            if data.get("mangaNewestContent")
            else data["mangaNewsectionName"],
            author=author,
        )

    @staticmethod
    def get_list(category=None, page=None):
        category = (
            0
            if category not in MHR.supported_categories
            else list(MHR.categories.keys())[
                list(MHR.categories.values()).index(category)
            ]
        )
        page = (page - 1) * 50 if page else 0

        query = {
            "subCategoryType": "0",
            "start": str(page),
            "limit": "50",
            "subCategoryId": str(category),
            "sort": "0",
            "gak": "android_manhuaren2",
        }
        query["gsn"] = MHR.hashGETQuery(query)

        response = requests.get(
            "https://hkmangaapi.manhuaren.com/v2/manga/getCategoryMangas?"
            + urllib.parse.urlencode(query),
            headers={"X-Yq-Yqci": '{"rn":"1080x1920","le":"tw"}'},
        ).json()

        try:
            manga = response["response"]["mangas"]
            result = []
            for i in manga:
                result.append(MHR.convert_to_simple(i))
            return result
        except:
            return []

    @staticmethod
    def get_details(ids: list, show_all: bool):
        if show_all:

            async def fetch_details():
                async def extract_details(session, id):
                    query = {
                        "mangaId": str(id),
                        "gak": "android_manhuaren2",
                    }

                    query["gsn"] = MHR.hashGETQuery(query)

                    response = (
                        await (
                            await session.get(
                                "https://hkmangaapi.manhuaren.com/v1/manga/getDetail?"
                                + urllib.parse.urlencode(query)
                            )
                        ).json()
                    )["response"]

                    def extract_episode(raw):
                        episodes = []
                        episodes_ids = []

                        for i in raw:
                            episodes.append(i["sectionName"])
                            episodes_ids.append(i["sectionId"])
                        return episodes, episodes_ids

                    serial, episodes_ids = extract_episode(response["mangaWords"])

                    extra, temp = extract_episode(response["mangaRolls"])
                    episodes_ids.extend(temp)

                    temp, temp2 = extract_episode(response["mangaEpisode"])
                    extra.extend(temp)
                    episodes_ids.extend(temp2)

                    categoriesText = response["mangaTheme"]
                    categories = []

                    for i in MHR.categoriesText.keys():
                        if categoriesText.find(i) != -1:
                            categories.append(MHR.categories[MHR.categoriesText[i]])

                    return Manga(
                        driver=MHR,
                        driver_data=MHRData(
                            episodes_ids=episodes_ids,
                            serial_len=len(serial),
                            manga_id=response["mangaId"],
                        ),
                        id=response["mangaId"],
                        title=response["mangaName"],
                        episodes=Episodes(serial=serial, extra=extra),
                        thumbnail=response["mangaPicimageUrl"],
                        is_end=bool(response["mangaIsOver"]),
                        author=response["mangaAuthors"],
                        description=response["mangaIntro"],
                        categories=categories,
                    )

                async with aiohttp.ClientSession(
                    headers={"X-Yq-Yqci": '{"rn":"1080x1920","le":"tw"}'}
                ) as session:
                    manga = []
                    for i in ids:
                        manga.append(asyncio.ensure_future(extract_details(session, i)))
                    return await asyncio.gather(*manga)

            return asyncio.run(fetch_details())
        else:
            query = {
                "gak": "android_manhuaren2",
            }

            body = {
                "bookIds": [],
                "mangaCoverimageType": 1,
                "mangaIds": ids,
                "somanIds": [],
            }

            query["gsn"] = MHR.hashPOSTQuery(body, query)

            response = requests.post(
                "https://hkmangaapi.manhuaren.com/v2/manga/getBatchDetail?"
                + urllib.parse.urlencode(query),
                json=body,
                headers={"X-Yq-Yqci": '{"rn":"1080x1920","le":"tw"}'},
            ).json()

            manga = response["response"]["mangas"]
            result = []
            for i in manga:
                result.append(MHR.convert_to_simple(i))
            return result

    @staticmethod
    def get_episode(episode: int, is_extra: bool, data: str):
        data_obj = MHRData.from_compressed(data)
        section_ids = data_obj.get_episode_ids(episode, is_extra)

        query = {
            "mangaSectionId": str(section_ids),
            "mangaId": str(data_obj.manga_id),
            "netType": "1",
            "loadreal": "1",
            "imageQuality": "2",
            "gak": "android_manhuaren2",
        }

        query["gsn"] = MHR.hashGETQuery(query)

        response = requests.get(
            "https://hkmangaapi.manhuaren.com/v1/manga/getRead?"
            + urllib.parse.urlencode(query),
            headers={"X-Yq-Yqci": '{"rn":"1080x1920","le":"tw"}'},
        ).json()["response"]

        base_url = response["hostList"][0]
        results = []

        for i in response["mangaSectionImages"]:
            results.append(base_url + i)

        return results

    @staticmethod
    def get_suggestion(text):
        query = {
            "keywords": chinese_converter.to_simplified(text),
            "gak": "android_manhuaren2",
        }

        query["gsn"] = MHR.hashGETQuery(query)

        response = requests.get(
            "https://hkmangaapi.manhuaren.com/v1/search/getKeywordMatch?"
            + urllib.parse.urlencode(query)
        ).json()["response"]["items"]

        result = []
        for i in response:
            result.append(i["mangaName"])

        return result

    def search(text, page=1):
        query = {
            "keywords": chinese_converter.to_simplified(text),
            "start": str((page - 1) * 50),
            "limit": "50",
            "gak": "android_manhuaren2",
        }

        query["gsn"] = MHR.hashGETQuery(query)

        response = requests.get(
            "https://hkmangaapi.manhuaren.com/v1/search/getSearchManga?"
            + urllib.parse.urlencode(query)
        ).json()["response"]

        ids = []
        for i in response["result"]:
            ids.append(i["mangaId"])

        return MHR.get_details(ids, False)
