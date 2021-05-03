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
    def get_content(url: str) -> bytes:
        response = get(url, verify=False, headers={
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        })

        if not response.ok:
            raise Exception(f"Got {response.status_code} when GETing {url}")

        return response.content

    def get_root_content(self):
        try:
            root_content = self.get_content(self.root)
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
        if substories is None:
            raise Exception("Bad substories selector")

        return substories

    def extract_headline(self, a: Tag, top_article=False) -> str:
        return a.text.strip()

    def valid_substory(self, a: Tag) -> bool:
        return True

    def is_premium(self, html: Tag, link: str) -> bool:
        return False

    def get_times(self, html: Tag, link: str) -> tuple[Optional[datetime], Optional[datetime]]:
        """
        :return: Tuple of published time and last updated time (if any)
        """
        return None, None

    def get_category(self, html: Tag, link: str) -> str:
        category = html.select_one(self.category_selector)
        if category is None:
            raise Exception(f"Couldn't get category for {link}")

        return normalize("NFKD", category.text)

    def __repr__(self):
        return f"<Source {self.name}>"
