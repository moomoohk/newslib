from abc import abstractmethod
from datetime import datetime
from typing import Optional
from unicodedata import normalize

from bs4.element import Tag


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
