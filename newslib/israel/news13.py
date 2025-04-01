import json
import re
from datetime import datetime
from functools import lru_cache

from bs4 import BeautifulSoup
from bs4.element import Tag

from newslib.source import Source


class News13Source(Source):
    def __init__(self):
        super().__init__(
            name="news13",
            root="https://13news.co.il/",
        )

        self.root = self._update_root()

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

    def _update_root(self):
        html = self.get_root_content()
        data = self.get_data(html)

        return data.get("props").get("pageProps").get("baseUrl")

    def get_times(self, url, html=None):
        post_data = self.get_post_data(url, html)

        published_text = post_data.get("publishDate")
        updated_text = post_data.get("updateDate")
        if None in (published_text, updated_text):
            raise Exception("Malformed JSON (missing times)")

        published = datetime.strptime(published_text, "%Y-%m-%d %H:%M:%S")
        updated = datetime.strptime(updated_text, "%Y-%m-%d %H:%M:%S")

        return published, updated

    @lru_cache(maxsize=10)
    def get_data(self, html: str):
        html = BeautifulSoup(html, "lxml")
        script = html.find("script", attrs={"id": "__NEXT_DATA__"})
        script = script.contents[0]

        return json.loads(str(script))

    def get_post_data(self, url, html=None):
        html, url = self.get_html(url, html)
        data = self.get_data(str(html))

        return data.get("props").get("pageProps").get("page").get("Content").get("Item")

    @lru_cache(maxsize=10)
    def get_articles(self, html: str):
        data = self.get_data(html).get("props").get("pageProps").get("page").get("Content").get("PageGrid")

        standard_four = next(filter(lambda grid_item: grid_item["grid_type"] == "standard_four", data))

        posts = standard_four.get("posts")
        if posts is None:
            raise Exception("Malformed JSON (no posts)")

        if len(posts) < 1:
            raise Exception("Posts list is too short")

        return posts

    @lru_cache(maxsize=10)
    def get_top_article(self, html: str):
        data = self.get_data(html).get("props").get("pageProps").get("page").get("Content").get("PageGrid")

        main_standard = next(filter(lambda grid_item: grid_item["grid_type"] == "MainStandard", data))

        main_posts = main_standard.get("posts")
        if main_posts is None:
            raise Exception("Malformed JSON (no MainStandard posts)")

        if len(main_posts) != 1:
            raise Exception(f"Expected 1 MainStandard post, got {len(main_posts)}")

        return main_posts[0]

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

        top_article = self.get_top_article(root_content)

        return self.create_a(top_article)

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

        category = post_data.get("category").get("name")
        if category is None:
            raise Exception("Malformed JSON (missing category)")

        return category
