from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup

from .models.driver import BaseDriver
from .models.manga import Manga, SimpleManga, Chapters, Chapter
from .util import get as cget


class MHG(BaseDriver):
    identifier = "MHG"
    categories = {
        "rexue": Manga.categories_list[0],
        "aiqing": Manga.categories_list[1],
        "xiaoyuan": Manga.categories_list[2],
        "baihe": Manga.categories_list[3],
        "danmei": Manga.categories_list[4],
        "maoxian": Manga.categories_list[5],
        "hougong": Manga.categories_list[6],
        "kehuan": Manga.categories_list[7],
        "zhanzheng": Manga.categories_list[8],
        "xuanyi": Manga.categories_list[9],
        "tuili": Manga.categories_list[10],
        "gaoxiao": Manga.categories_list[11],
        "mohuan": Manga.categories_list[12],
        "mofa": Manga.categories_list[13],
        "kongbu": Manga.categories_list[14],
        "shengui": Manga.categories_list[15],
        "lishi": Manga.categories_list[16],
        "jingji": Manga.categories_list[18],
        "jizhan": Manga.categories_list[20],
        "weiniang": Manga.categories_list[22],
    }
    supported_categories = list(categories.values())
    recommended_chunk_size = 5
    proxy_settings = {
        "genre": {"thumbnail": [], "manga": []},
        "headers": {"referer": "https://tw.manhuagui.com"},
    }

    @staticmethod
    def get_details(ids: list, show_all: bool):
        if len(ids) > 6:
            length = len(ids)
            return MHG.get_details(ids[: length // 2]) + MHG.get_details(
                ids[length // 2 :]
            )

        session = requests.Session()

        def extract_details(id):
            text = cget(session, f"https://tw.manhuagui.com/comic/{id}/")

            soup = BeautifulSoup(text, "lxml")
            thumbnail = soup.find("p", class_="hcover")
            is_end = "finish" in thumbnail.find_all("span")[-1]["class"]
            thumbnail = "https:" + thumbnail.find("img")["src"]

            title = soup.find("div", class_="book-title").find("h1").text.strip()
            info = soup.find("ul", class_="detail-list cf").find_all("li")
            categories = [
                MHG.categories[i["href"][6:-1]]
                for i in info[1].find("span").find_all("a")
                if i["href"][6:-1] in MHG.categories.keys()
            ]
            author = [i.text.strip() for i in info[1].find_all("span")[1].find_all("a")]
            description = soup.find("div", id="intro-cut").text.strip()

            chapter_list = soup.find_all("div", class_="chapter-list")

            def extract_chapter(raw):
                try:
                    chapters = []
                    for i in reversed(raw.find_all("ul")):
                        for j in i.find_all("a"):
                            chapters.append(
                                Chapter(
                                    title=j["title"].strip(),
                                    id=j["href"].replace(id, "")[8:-5],
                                )
                            )
                    return chapters
                except:
                    return []

            serial = extract_chapter(chapter_list[0])
            extra = []
            for i in chapter_list[1:]:
                extra.extend(extract_chapter(i))

            manga = Manga(
                driver=MHG,
                id=id,
                chapters=Chapters(serial=serial, extra=extra, extra_data=id),
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
    def get_chapter(id: str, extra_data: str):
        details = get(f"https://tw.manhuagui.com/comic/{extra_data}/{id}.html")
        urls = list(
            map(
                lambda x: f"https://i.hamreus.com{details['path']}{x}", details["files"]
            )
        )

        return urls

    @staticmethod
    def get_list(category: str, page: int):
        category = (
            ""
            if category not in MHG.supported_categories
            else list(MHG.categories.keys())[
                list(MHG.categories.values()).index(category)
            ]
            + "/"
        )
        page = f"index_p{page if page else 1}.html"

        response = requests.get(
            f"https://tw.manhuagui.com/list/{category}{page}",
        )
        soup = BeautifulSoup(response.text, "lxml")

        result = []
        for i in soup.find("ul", id="contList").find_all("li"):
            details = i.find("a")
            id = details["href"][7:-1]
            try:
                src = details.find("img")["src"]
            except:
                src = details.find("img")["data-src"]
            thumbnail = "https:" + src

            latest = (
                details.find("span", class_="tt")
                .text.replace("更新至", "")
                .replace("[完]", "")
                .strip()
            )
            is_end = "fd" in details.find_all("span")[-1]["class"]
            title = i.find("p").find("a").text.strip()

            result.append(
                SimpleManga(
                    driver=MHG,
                    id=id,
                    title=title,
                    thumbnail=thumbnail,
                    is_end=is_end,
                    latest=latest,
                )
            )

        return result

    @staticmethod
    def search(text, page=1):
        response = requests.get(
            f"https://tw.manhuagui.com/s/{text}_p{page}.html",
        )
        soup = BeautifulSoup(response.text, "lxml")

        current = soup.find("span", class_="current")
        if (not current and page != 1) or (current and int(current.text) != page):
            return []

        result = []
        for i in soup.find_all("li", class_="cf"):
            details = i.find("a")
            id = details["href"][7:-1]
            try:
                src = details.find("img")["src"]
            except:
                src = details.find("img")["data-src"]
            thumbnail = "https:" + src

            title = i.find("dt").find("a").text.strip()
            is_end = i.find("dd").find("span")
            latest = is_end.find("a").text.strip()
            is_end = is_end.find("span").text == "已完结"

            result.append(
                SimpleManga(
                    driver=MHG,
                    id=id,
                    title=title,
                    thumbnail=thumbnail,
                    is_end=is_end,
                    latest=latest,
                )
            )

        return result

    @staticmethod
    def check_online() -> bool:
        try:
            requests.get("https://tw.manhuagui.com/", timeout=5)
            return True
        except:
            return False


# Development by HSSLCreative
# link: https://github.com/HSSLC/manhuagui-dlr
# Modified for this project

import re, json, lzstring

lz = lzstring.LZString()


# get.py
def get(url):
    try:
        res = requests.get(url)
    except:
        return False
    m = re.match(r"^.*\}\(\'(.*)\',(\d*),(\d*),\'([\w|\+|\/|=]*)\'.*$", res.text)
    return packed(
        m.group(1),
        int(m.group(2)),
        int(m.group(3)),
        lz.decompressFromBase64(m.group(4)).split("|"),
    )


# parse.py
def packed(functionFrame, a, c, data):
    def e(innerC):
        return ("" if innerC < a else e(int(innerC / a))) + (
            chr(innerC % a + 29) if innerC % a > 35 else tr(innerC % a, 36)
        )

    c -= 1
    d = {}
    while c + 1:
        d[e(c)] = e(c) if data[c] == "" else data[c]
        c -= 1
    pieces = re.split(r"(\b\w+\b)", functionFrame)
    js = "".join([d[x] if x in d else x for x in pieces]).replace("\\'", "'")
    return json.loads(re.search(r"^.*\((\{.*\})\).*$", js).group(1))


# tran.py
def itr(value, num):
    d = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "" if value <= 0 else itr(int(value / num), num) + d[value % num]


def tr(value, num):
    tmp = itr(value, num)
    return "0" if tmp == "" else tmp
