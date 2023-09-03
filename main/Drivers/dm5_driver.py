from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import js2py
import chinese_converter

from .classes.driver import Chapters, BaseDriver, BaseDriverData
from .classes.manga import Manga, SimpleManga
from .util import get, use_proxy


@dataclass
class DM5Data(BaseDriverData):
    chapters_urls: list
    serial_len: int

    @property
    def dict(self):
        return {"chapters_urls": self.chapters_urls, "serial_len": self.serial_len}

    @staticmethod
    def from_dict(dict):
        return DM5Data(
            chapters_urls=dict["chapters_urls"], serial_len=dict["serial_len"]
        )

    @staticmethod
    def from_compressed(compressed):
        return DM5Data._from_compresssed(DM5Data, compressed)


class DM5(BaseDriver):
    identifier = "DM5"
    categories = {
        "rexue": Manga.categories_list[0],
        "aiqing": Manga.categories_list[1],
        "xiaoyuan": Manga.categories_list[2],
        "baihe": Manga.categories_list[3],
        "caihong": Manga.categories_list[4],
        "maoxian": Manga.categories_list[5],
        "hougong": Manga.categories_list[6],
        "kehuan": Manga.categories_list[7],
        "zhanzheng": Manga.categories_list[8],
        "xuanyi": Manga.categories_list[9],
        "zhentan": Manga.categories_list[10],
        "gaoxiao": Manga.categories_list[11],
        "qihuan": Manga.categories_list[12],
        "mofa": Manga.categories_list[13],
        "kongbu": Manga.categories_list[14],
        "dongfangshengui": Manga.categories_list[15],
        "lishi": Manga.categories_list[16],
        "tongren": Manga.categories_list[17],
        "jingji": Manga.categories_list[18],
        "jiecao": Manga.categories_list[19],
        "jizhan": Manga.categories_list[20],
        "list-tag61": Manga.categories_list[21],
    }
    supported_categories = list(categories.values())
    support_suggestion = True
    recommended_chunk_size = 10
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

    @staticmethod
    def get_details(ids: list, show_all: bool, proxy: bool):
        session = requests.Session()
        session.headers = {"Accept-Language": "en-US,en;q=0.5"}
        session.cookies.set("isAdult", "1")

        def extract_details(id):
            text = get(session, f"https://www.dm5.com/manhua-{id}/")

            soup = BeautifulSoup(text, "lxml")
            info = soup.find("div", class_="info")

            title = (
                info.find("p", class_="title").find(text=True, recursive=False).strip()
            )
            author = [
                i.text.strip() for i in info.find("p", class_="subtitle").find_all("a")
            ]
            description = (
                info.find("p", class_="content")
                .text.replace("[+展开]", "")
                .replace("[-折叠]", "")
                .strip()
            )
            thumbnail = soup.find("div", "cover").find("img")["src"]
            if proxy:
                thumbnail = use_proxy(DM5.identifier, thumbnail, "thumbnail")

            tip = info.find("p", class_="tip")
            is_end = tip.find("span", class_="").text != "连载中"
            categories = [
                DM5.categories[i["href"][8:-1]]
                for i in tip.find_all("a")
                if i["href"][8:-1] in DM5.categories.keys()
            ]

            def extract_chapter(raw):
                try:
                    chapters = []
                    chapters_urls = []
                    for i in raw.findChildren("a"):
                        title = i.find(text=True, recursive=False).strip()
                        chapters.append(title)
                        chapters_urls.append(i["href"])
                    return chapters, chapters_urls
                except:
                    return [], []

            serial, chapters_urls = extract_chapter(
                soup.find("ul", id="detail-list-select-1")
            )

            extra = []
            extra_id = ("detail-list-select-2", "detail-list-select-3")
            for i in extra_id:
                raw = soup.find("ul", id=i)
                if raw:
                    result = extract_chapter(raw)
                    extra.extend(result[0])
                    chapters_urls.extend(result[1])

            manga = Manga(
                driver=DM5,
                driver_data=DM5Data(
                    chapters_urls=chapters_urls,
                    serial_len=len(serial),
                ),
                id=id,
                chapters=Chapters(serial=serial, extra=extra),
                thumbnail=thumbnail,
                title=title,
                author=author,
                description=description,
                is_end=is_end,
                categories=categories,
            )

            return manga if show_all else manga.to_simple

        def fetch_details():
            with ThreadPoolExecutor(max_workers=10) as pool:
                manga = list(pool.map(extract_details, ids))
            return manga

        return fetch_details()

    @staticmethod
    def __extract_small_preview(item):
        title = item.find("h2", class_="title").find("a")
        id = title["href"][8:-1]
        title = title.text.strip()
        thumbnail = item.find("p", class_="mh-cover")["style"][22:-1]
        latest = item.find("p", class_="chapter")
        is_end = latest.find("span").text.strip() == "完结"
        latest = latest.find("a").text.strip()
        author = [j.text.strip() for j in item.find("p", class_="author").find_all("a")]
        return SimpleManga(
            driver=DM5,
            id=id,
            title=title,
            thumbnail=thumbnail,
            is_end=is_end,
            latest=latest,
            author=author,
        )

    @staticmethod
    def get_chapter(chapter: int, is_extra: bool, data: str, proxy: bool):
        data = DM5Data.from_compressed(data)
        url = data.chapters_urls[chapter + (data.serial_len if is_extra else 0)]
        body = requests.get(
            f"https://www.manhuaren.com/{url}/",
            headers={"Accept-Language": "en-US,en;q=0.5"},
        ).text

        def find_between(s, start, end):
            start_p = s.find(start) + len(start) - 1
            return s[start_p : s.find(end, start_p) + 1]

        lst_str = js2py.eval_js(find_between(body, "eval(", ")\n</script>"))
        result = find_between(lst_str, "['", "'];").replace("'", "").split(",")

        if proxy:
            result = map(lambda x: use_proxy(DM5.identifier, x, "manga"), result)

        return result

    @staticmethod
    def get_list(category: str, page: int, proxy: bool):
        category = (
            "list"
            if category not in DM5.supported_categories
            else list(DM5.categories.keys())[
                list(DM5.categories.values()).index(category)
            ]
        )
        page = f"-p{page}" if page else ""

        response = requests.get(
            f"https://www.dm5.com/manhua-{category}{page}/",
            headers={"Accept-Language": "en-US,en;q=0.5"},
        )
        soup = BeautifulSoup(response.text, "lxml")

        result = []
        for i in soup.find("ul", class_="mh-list col7").find_all(
            "div", class_="mh-item"
        ):
            simple = DM5.__extract_small_preview(i)
            if proxy:
                simple.thumbnail = use_proxy(
                    DM5.identifier, simple.thumbnail, "thumbnail"
                )
            result.append(simple)

        return result

    @staticmethod
    def get_suggestion(text):
        response = requests.get(
            f"https://www.dm5.com/search.ashx?t={chinese_converter.to_simplified(text)}/",
            headers={"Accept-Language": "en-US,en;q=0.5"},
        )
        soup = BeautifulSoup(response.text, "lxml")

        return [i.text.strip() for i in soup.find_all("span", class_="left")]

    @staticmethod
    def search(text, page=1, proxy=False):
        response = requests.get(
            f"https://www.dm5.com/search?title={chinese_converter.to_simplified(text)}&page={page}",
            headers={"Accept-Language": "en-US,en;q=0.5"},
        )
        soup = BeautifulSoup(response.text, "lxml")

        result = []
        huge = soup.find("div", class_="banner_detail_form")
        if huge:
            thumbnail = huge.find("img")["src"]
            if proxy:
                thumbnail = use_proxy(DM5.identifier, thumbnail, "thumbnail")

            title = huge.find("p", class_="title").find("a")
            id = title["href"][8:-1]
            title = title.text.strip()
            is_end = huge.find("span", class_="block").find("span").text != "连载中"
            latest = (
                huge.find("div", class_="bottom")
                .find("a", class_="btn-2")["title"]
                .replace(title, "")[1:]
            )
            author = [
                i.text.strip() for i in huge.find("p", class_="subtitle").find_all("a")
            ]
            result.append(
                SimpleManga(
                    driver=DM5,
                    id=id,
                    title=title,
                    thumbnail=thumbnail,
                    is_end=is_end,
                    latest=latest,
                    author=author,
                )
            )

        for i in soup.find("ul", class_="mh-list col7").find_all(
            "div", class_="mh-item"
        ):
            simple = DM5.__extract_small_preview(i)
            if proxy:
                simple.thumbnail = use_proxy(
                    DM5.identifier, simple.thumbnail, "thumbnail"
                )
            result.append(simple)

        return result

    @staticmethod
    def check_online() -> bool:
        try:
            requests.get("https://www.dm5.com", timeout=5)
            return True
        except:
            return False
