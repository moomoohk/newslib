import json
import re
from datetime import datetime
from functools import cache

from bs4.element import Tag

from newslib.source import Source


class News13Source(Source):
    def __init__(self):
        super().__init__(
            name="news13",
            root="https://13news.co.il/",
        )

        self.data_query_re = re.compile(r"window\.data_query = (?P<data>.+?)\.data_query")

    @property
    def top_article_selector(self) -> str:
        raise NotImplemented

    @property
    def substories_selector(self) -> str:
        raise NotImplemented

    @property
    def category_selector(self) -> str:
        raise NotImplemented

    @property
    def published_selector(self) -> str:
        raise NotImplemented

    def get_times(self, url, html=None):
        post_data = self.get_post_data(url, html)

        published_timestamp = post_data.get("publishDate_t")
        updated_timestamp = post_data.get("updateDate_t")
        if None in (published_timestamp, updated_timestamp):
            raise Exception("Malformed JSON (missing times)")

        published = datetime.fromtimestamp(published_timestamp / 1000)
        updated = None if updated_timestamp == "" else datetime.fromtimestamp(updated_timestamp / 1000)

        return published, updated

    @cache
    def get_data(self, html: str):
        match = re.search(self.data_query_re, html)
        if not match:
            raise Exception("Couldn't extract article data")

        return json.loads(match["data"])

    def get_post_data(self, url, html=None):
        html = self.get_html(url, html)
        data = self.get_data(str(html))

        post_id = data["header"].get("post_id")
        if post_id is None:
            raise Exception("Malformed JSON (missing post ID)")

        post_data = data["items"].get(str(post_id))
        if post_data is None:
            raise Exception("Malformed JSON (missing post data)")

        return post_data

    @cache
    def get_articles(self, html: str):
        data = self.get_data(html)

        blocks = data.get("blocks")
        if blocks is None:
            raise Exception("Malformed JSON (no blocks)")

        if len(blocks) < 1:
            raise Exception("Blocks list is too short")

        main_block_posts = blocks[0].get("Posts")
        if main_block_posts is None:
            raise Exception("Malformed JSON (no main block posts)")

        items = data.get("items")
        if items is None:
            raise Exception("Malformed JSON (no items)")

        return [items[str(post_id)] for post_id in main_block_posts]

    @staticmethod
    def create_a(article_data: dict):
        article_link = article_data.get("link")
        article_title = article_data.get("title")
        if not all((article_link, article_title)):
            raise Exception("Malformed JSON (missing article data)")

        a = Tag(name="a", attrs={"href": article_link})
        a.string = article_title

        return a

    def get_top_article_a(self, root_content=None) -> Tag:
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

    def get_substories_a(self, root_content=None) -> list[Tag]:
        if root_content is None:
            root_content = self.get_root_content()

        elif isinstance(root_content, Tag):
            root_content = str(root_content)

        elif isinstance(root_content, bytes):
            root_content = root_content.decode()

        articles = self.get_articles(root_content)
        if len(articles) < 5:
            raise Exception("Articles list too short")

        articles.pop(0)

        substories = []
        for article in articles:
            substories.append(self.create_a(article))

        return substories

    def get_category(self, url, html=None) -> str:
        post_data = self.get_post_data(url, html)

        category = post_data.get("CategoryLabel")
        if category is None:
            raise Exception("Malformed JSON (missing category)")

        return category
