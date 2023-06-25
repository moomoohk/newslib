import json
import re
from datetime import datetime
from functools import lru_cache
from urllib.parse import unquote

from bs4.element import Tag
from lzstring import LZString

from newslib.source import Source


class WallaSource(Source):
    def __init__(self):
        super().__init__(
            name="walla",
            root="https://news.walla.co.il/",
            rss_news_link="https://rss.walla.co.il/feed/1?type=main",
            rss_news_flashes="https://rss.walla.co.il/feed/22",
            rss_guid="link",
            rss_datetime_format="%a, %d %b %Y %H:%M:%S %Z",
            tags_selector="#container > section.fc.common-section.grid-1-1.sticky-content-will-change-position > "
                          "section > article > section.tags.target-editorial > ul > li > a",
        )

        self.data_query_re = re.compile(r"window\.loadDataState = \"(?P<data>.+?)\"")

    @property
    def top_article_selector(self) -> str:
        raise NotImplementedError

    @property
    def substories_selector(self) -> str:
        raise NotImplementedError

    @property
    def category_selector(self) -> str:
        raise NotImplementedError

    @property
    def published_selector(self) -> str:
        raise NotImplementedError

    @lru_cache(maxsize=10)
    def get_data(self, html: str):
        match = re.search(self.data_query_re, html)
        if not match:
            raise Exception("Couldn't extract article data")

        data = LZString().decompressFromBase64(match["data"])
        data = unquote(data)
        return json.loads(data)

    def get_post_data(self, url: str, html=None):
        html = self.get_html(url, html)
        data = self.get_data(str(html))

        article_id = re.match(r"https://news\.walla\.co\.il/item/(?P<id>\d+)", url)["id"]

        return data.get(f"Item_{article_id}").get("data").get("item").get("data")

    @lru_cache(maxsize=10)
    def get_articles(self, html: str):
        data = self.get_data(html)

        articles = data.get("***Editor_3").get("data").get("editor").get("data").get("events")
        if not articles:
            raise Exception("Malformed JSON (no articles)")

        return articles

    @staticmethod
    def create_a(article_data: dict):
        article_link = article_data.get("canonical").get("url")
        article_title = article_data.get("title")
        if not all((article_link, article_title)):
            raise Exception("Malformed JSON (missing article data)")

        a = Tag(name="a", attrs={"href": article_link})
        a.string = article_title

        return a

    def get_top_article_a(self, root_content=None):
        if root_content is None:
            root_content = self.get_root_content()

        elif isinstance(root_content, Tag):
            root_content = str(root_content)

        elif isinstance(root_content, bytes):
            root_content = root_content.decode()

        articles = self.get_articles(root_content)
        if len(articles) < 1:
            raise Exception("Articles list too short")

        return self.create_a(articles[0])

    def get_substories_a(self, root_content=None):
        if root_content is None:
            root_content = self.get_root_content()

        elif isinstance(root_content, Tag):
            root_content = str(root_content)

        elif isinstance(root_content, bytes):
            root_content = root_content.decode()

        articles = self.get_articles(root_content)
        if len(articles) < 1:
            raise Exception("Articles list too short")

        articles.pop(0)

        substories = []
        for article in articles:
            substories.append(self.create_a(article))

        return substories

    def get_times(self, url, html=None):
        post_data = self.get_post_data(url, html)

        publish_date = datetime.fromtimestamp(post_data.get("unix_publication_date"))
        update_date = datetime.fromtimestamp(post_data.get("unix_update_date"))
        return publish_date, update_date

    def get_category(self, url, html=None) -> str:
        post_data = self.get_post_data(url, html)
        category = post_data.get("canonical").get("display").get("name")
        if category is None:
            raise Exception("Malformed JSON (missing category)")

        return category
