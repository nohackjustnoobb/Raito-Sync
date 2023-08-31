from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import hashlib
import re
import urllib.parse
import requests
import json
import chinese_converter

from .util import use_proxy
from .classes.driver import Chapters, BaseDriver, BaseDriverData
from .classes.manga import Manga, SimpleManga


@dataclass
class MHRData(BaseDriverData):
    manga_id: str
    chapters_ids: list
    serial_len: int

    def get_chapter_ids(self, chapter, is_extra):
        return self.chapters_ids[chapter + self.serial_len if is_extra else chapter]

    @property
    def dict(self):
        return {
            "chapters_urls": self.chapters_ids,
            "serial_len": self.serial_len,
            "manga_id": self.manga_id,
        }

    @staticmethod
    def from_dict(dict):
        return MHRData(
            chapters_ids=dict["chapters_urls"],
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
        "爱情": 26,
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
    proxy_settings = {
        "genre": {
            "thumbnail": [
                "https://mhfm1us.cdnmanhua.net",
                "https://mhfm2us.cdnmanhua.net",
                "https://mhfm3us.cdnmanhua.net",
                "https://mhfm4us.cdnmanhua.net",
                "https://mhfm5us.cdnmanhua.net",
                "https://mhfm6us.cdnmanhua.net",
                "https://mhfm7us.cdnmanhua.net",
                "https://mhfm8us.cdnmanhua.net",
                "https://mhfm9us.cdnmanhua.net",
                "https://mhfm10us.cdnmanhua.net",
            ],
            "manga": [],
        },
        "headers": {},
    }
    headers = {
        "Authorization": "YINGQISTS2 eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc19mcm9tX3JndCI6ZmFsc2UsInVzZXJfbGVnYWN5X2lkIjo0NjIwOTk4NDEsImRldmljZV9pZCI6Ii0zNCw2OSw2MSw4MSw2LDExNCw2MSwtMzUsLTEsNDgsNiwzNSwtMTA3LC0xMjIsLTExLC04NywxMjcsNjQsLTM4LC03LDUwLDEzLC05NCwtMTcsLTI3LDkyLC0xNSwtMTIwLC0zNyw3NCwtNzksNzgiLCJ1dWlkIjoiOTlmYTYzYjQtNjFmNy00ODUyLThiNDMtMjJlNGY3YzY2MzhkIiwiY3JlYXRldGltZV91dGMiOiIyMDIzLTA3LTAzIDAyOjA1OjMwIiwibmJmIjoxNjg4MzkzMTMwLCJleHAiOjE2ODgzOTY3MzAsImlhdCI6MTY4ODM5MzEzMH0.IJAkDs7l3rEvURHiy06Y2STyuiIu-CYUk5E8en4LU0_mrJ83hKZR1nVqKiAY9ry_6ZmFzVfg-ap_TXTF6GTqihyM-nmEpD2NVWeWZ5VHWVgJif4ezB4YTs0YEpnVzYCk_x4p0wU2GYbqf1BFrNO7PQPMMPDGfaCTUqI_Pe2B0ikXMaN6CDkMho26KVT3DK-xytc6lO92RHvg65Hp3xC1qaonQXdws13wM6WckUmrswItroy9z38hK3w0rQgXOK2mu3o_4zOKLGfq5JpqOCNQCLJgQ0_jFXhMtaz6E_fMZx54fZHfF1YrA-tfs7KFgiYxMb8PnNILoniFrQhvET3y-Q",
        "X-Yq-Yqci": '{"av":"1.3.8","cy":"HK","lut":"1662458886867","nettype":1,"os":2,"di":"733A83F2FD3B554C3C4E4D46A307D560A52861C7","fcl":"appstore","fult":"1662458886867","cl":"appstore","pi":"","token":"","fut":"1662458886867","le":"en-HK","ps":"1","ov":"16.4","at":2,"rn":"1668x2388","ln":"","pt":"com.CaricatureManGroup.CaricatureManGroup","dm":"iPad8,6"}',
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; sdk_gphone64_arm64 Build/SE1A.220630.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Mobile Safari/537.36",
    }
    extra_query = {
        "gak": "android_manhuaren2",
        "gaui": "462099841",
        "gft": "json",
        "gui": "462099841",
    }

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
    def change_to_faster_source(url):
        return url.replace("cdndm5.com", "cdnmanhua.net")

    @staticmethod
    def convert_to_simple(data):
        author = re.split("，| |  ", data["mangaAuthor"])
        author = [s for s in author if s]

        return SimpleManga(
            driver=MHR,
            id=str(data["mangaId"]),
            title=data["mangaName"],
            thumbnail=MHR.change_to_faster_source(data["mangaCoverimageUrl"]),
            is_end=bool(data["mangaIsOver"]),
            latest=data["mangaNewestContent"]
            if data.get("mangaNewestContent")
            else data["mangaNewsectionName"],
            author=author,
        )

    @staticmethod
    def get_list(category: str, page: int, proxy: bool):
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
            **MHR.extra_query,
        }
        query["gsn"] = MHR.hashGETQuery(query)

        response = requests.get(
            "https://hkmangaapi.manhuaren.com/v2/manga/getCategoryMangas?"
            + urllib.parse.urlencode(query),
            headers=MHR.headers,
        ).json()

        try:
            manga = response["response"]["mangas"]
            result = []
            for i in manga:
                simple = MHR.convert_to_simple(i)
                if proxy:
                    simple.thumbnail = use_proxy(
                        MHR.identifier, simple.thumbnail, "thumbnail"
                    )
                result.append(simple)
            return result
        except:
            return []

    @staticmethod
    def get_details(ids: list, show_all: bool, proxy: bool):
        if show_all:
            session = requests.Session()
            session.headers = MHR.headers

            def fetch_details():
                def extract_details(id):
                    query = {
                        "mangaId": str(id),
                        "mangaDetailVersion": "",
                        **MHR.extra_query,
                    }
                    query["gsn"] = MHR.hashGETQuery(query)

                    response = session.get(
                        "https://hkmangaapi.manhuaren.com/v1/manga/getDetail?"
                        + urllib.parse.urlencode(query)
                    ).json()["response"]

                    def extract_chapter(raw):
                        chapters = []
                        chapters_ids = []

                        for i in raw:
                            chapters.append(i["sectionName"])
                            chapters_ids.append(i["sectionId"])
                        return chapters, chapters_ids

                    serial, chapters_ids = extract_chapter(response["mangaWords"])

                    extra, temp = extract_chapter(response["mangaRolls"])
                    chapters_ids.extend(temp)

                    temp, temp2 = extract_chapter(response["mangaEpisode"])
                    extra.extend(temp)
                    chapters_ids.extend(temp2)

                    categoriesText = response["mangaTheme"]
                    categories = []

                    for i in MHR.categoriesText.keys():
                        if categoriesText.find(i) != -1:
                            categories.append(MHR.categories[MHR.categoriesText[i]])

                    thumbnail = MHR.change_to_faster_source(
                        response["mangaPicimageUrl"]
                    )

                    if proxy:
                        thumbnail = use_proxy(MHR.identifier, thumbnail, "thumbnail")

                    return Manga(
                        driver=MHR,
                        driver_data=MHRData(
                            chapters_ids=chapters_ids,
                            serial_len=len(serial),
                            manga_id=str(response["mangaId"]),
                        ),
                        id=str(response["mangaId"]),
                        title=response["mangaName"],
                        chapters=Chapters(serial=serial, extra=extra),
                        thumbnail=thumbnail,
                        is_end=bool(response["mangaIsOver"]),
                        author=response["mangaAuthors"],
                        description=response["mangaIntro"],
                        latest=response["mangaNewsectionName"],
                        categories=categories,
                    )

                with ThreadPoolExecutor(max_workers=10) as pool:
                    manga = list(pool.map(extract_details, ids))
                return manga

            return fetch_details()
        else:
            query = MHR.extra_query.copy()

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
                headers=MHR.headers,
            ).json()

            manga = response["response"]["mangas"]
            result = []
            for i in manga:
                simple = MHR.convert_to_simple(i)
                if proxy:
                    simple.thumbnail = use_proxy(
                        MHR.identifier, simple.thumbnail, "thumbnail"
                    )
                result.append(simple)

            return result

    @staticmethod
    def get_chapter(chapter: int, is_extra: bool, data: str, proxy: bool):
        data_obj = MHRData.from_compressed(data)
        section_ids = data_obj.get_chapter_ids(chapter, is_extra)

        query = {
            "mangaSectionId": str(section_ids),
            "mangaId": str(data_obj.manga_id),
            "netType": "1",
            "loadreal": "1",
            "imageQuality": "2",
            **MHR.extra_query,
        }

        query["gsn"] = MHR.hashGETQuery(query)

        response = requests.get(
            "https://hkmangaapi.manhuaren.com/v1/manga/getRead?"
            + urllib.parse.urlencode(query),
            headers=MHR.headers,
        ).json()["response"]

        base_url = response["hostList"][0]
        results = []

        for i in response["mangaSectionImages"]:
            url = base_url + i
            if proxy:
                url = use_proxy(MHR.identifier, url, "manga")

            results.append(url)

        return results

    @staticmethod
    def get_suggestion(text):
        query = {
            "keywords": chinese_converter.to_simplified(text.replace("/", "")),
            "mh_is_anonymous": "0",
            **MHR.extra_query,
        }

        query["gsn"] = MHR.hashGETQuery(query)

        response = requests.get(
            "https://hkmangaapi.manhuaren.com/v1/search/getKeywordMatch?"
            + urllib.parse.urlencode(query),
            headers=MHR.headers,
        ).json()["response"]["items"]

        result = []
        for i in response:
            result.append(i["mangaName"])

        return result

    @staticmethod
    def search(text, page=1, proxy=False):
        query = {
            "keywords": chinese_converter.to_simplified(text.replace("/", "")),
            "start": str((page - 1) * 50),
            "limit": "50",
            **MHR.extra_query,
        }

        query["gsn"] = MHR.hashGETQuery(query)

        response = requests.get(
            "https://hkmangaapi.manhuaren.com/v1/search/getSearchManga?"
            + urllib.parse.urlencode(query),
            headers=MHR.headers,
        ).json()["response"]

        ids = []
        for i in response["result"]:
            ids.append(i["mangaId"])

        return MHR.get_details(ids, False, proxy)

    @staticmethod
    def check_online() -> bool:
        try:
            requests.get("https://hkmangaapi.manhuaren.com", timeout=5)
            return True
        except:
            return False
