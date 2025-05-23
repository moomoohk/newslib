from abc import abstractmethod
from datetime import datetime
from typing import Optional, Union
from unicodedata import normalize

from bs4 import BeautifulSoup
from bs4.element import Tag
from requests import get

from newslib import logger


class Source:
    def __init__(
            self,
            name: str,
            root: str,
            rss_news_link: str = None,
            rss_news_flashes: str = None,
            rss_guid="guid",
            rss_tags_name="tags",
            rss_created_tag="pubDate",
            rss_modified_tag: str = None,
            rss_datetime_format="%a, %d %b %Y %H:%M:%S %z",
            include_query_string=False,
            tags_selector: str = None,
    ):
        self.name = name
        self.root = root

        self.rss_news_link = rss_news_link
        self.rss_news_flashes = rss_news_flashes

        self.rss_guid = rss_guid
        self.rss_tags_name = rss_tags_name
        self.rss_created_tag = rss_created_tag
        self.rss_modified_tag = rss_modified_tag
        self.rss_datetime_format = rss_datetime_format
        self.include_query_string = include_query_string
        self.tags_selector = tags_selector

    @property
    @abstractmethod
    def top_article_selector(self) -> str:
        pass

    @property
    @abstractmethod
    def substories_selector(self) -> str:
        pass

    @property
    @abstractmethod
    def category_selector(self) -> str:
        pass

    @property
    @abstractmethod
    def published_selector(self) -> str:
        pass

    def check_rss_error(self, feed: Tag):
        pass

    def get_rss_item_tags(self, item: Tag) -> list[str]:
        tags = item.find(self.rss_tags_name)

        if tags is not None:
            return [tag.strip() for tag in tags.text.split(",")]

        return []

    @staticmethod
    def get_content(url: str) -> tuple[bytes, str]:
        response = get(url, verify=False, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/89.0.4389.90 Safari/537.36 "
            # "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        })

        if not response.ok:
            raise Exception(f"Got {response.status_code} when GETing {url}")

        return response.content, response.url

    @staticmethod
    def get_html(url, html: Union[Tag, str, bytes] = None) -> tuple[Tag, str]:
        if html is None:
            content, url = Source.get_content(url)
            html = BeautifulSoup(content, "lxml")

            if len(html.body) == 0:
                raise Exception("Empty body received")

        return html, url

    def get_root_content(self) -> bytes:
        try:
            root_content, _ = self.get_content(self.root)
        except Exception:
            logger.error("Couldn't GET root content")
            raise

        return root_content

    def get_top_article_a(self, root_content: Union[str, bytes, Tag] = None) -> Tag:
        if root_content is None:
            root_content = self.get_root_content()

        if not isinstance(root_content, Tag):
            root_content = BeautifulSoup(root_content, "lxml")

        top_article_a = root_content.select_one(self.top_article_selector)
        if top_article_a is None:
            raise Exception("Bad top article selector")

        return top_article_a

    def get_substories_a(self, root_content: Union[str, bytes, Tag] = None) -> list[Tag]:
        if root_content is None:
            root_content = self.get_root_content()

        if not isinstance(root_content, Tag):
            root_content = BeautifulSoup(root_content, "lxml")

        substories = root_content.select(self.substories_selector)
        if not substories:
            raise Exception("Bad substories selector")

        return substories

    def get_headline(self, a: Tag, top_article=False) -> str:
        return a.text.strip()

    def valid_substory(self, a: Tag) -> bool:
        return True

    def is_premium(self, url: str, html: Tag = None) -> bool:
        return False

    def get_times(self, url: str, html: Tag = None) -> tuple[Optional[datetime], Optional[datetime]]:
        """
        :return: Tuple of published time and last updated time (if any)
        """
        return None, None

    def get_tags(self, url: str, html: Tag = None) -> Optional[list[str]]:
        if self.tags_selector is None:
            return None

        html, url = self.get_html(url, html)

        tags_a = html.select(self.tags_selector)
        return [a.text for a in tags_a]

    def get_category(self, url: str, html: Tag = None) -> str:
        html, url = self.get_html(url, html)

        category = html.select_one(self.category_selector)
        if category is None:
            raise Exception(f"Couldn't get category for {url}")

        return normalize("NFKD", category.text)

    def __repr__(self):
        return f"<Source {self.name}>"
