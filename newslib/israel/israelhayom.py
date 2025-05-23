import json
from datetime import datetime

from bs4 import BeautifulSoup
from bs4.element import Tag

from newslib.source import Source


class IsraelHayomSource(Source):
    def __init__(self):
        super().__init__(
            name="israelhayom",
            root="https://www.israelhayom.co.il/news",
            rss_news_link="https://www.israelhayom.co.il/rss.xml",
            tags_selector="a.single-post-tag",
        )

    @property
    def top_article_selector(self) -> str:
        raise NotImplementedError

    @property
    def substories_selector(self) -> str:
        raise NotImplementedError

    @property
    def category_selector(self) -> str:
        return ".breadcrumbs > li:last-child > a"

    @property
    def published_selector(self) -> str:
        return ".single-post-meta-dates time"

    @staticmethod
    def create_a(article_data: dict):
        article_link = article_data.get("permalink")
        article_title = article_data.get("titles").get("title")
        if not all((article_link, article_title)):
            raise Exception("Malformed JSON (missing article data)")

        a = Tag(name="a", attrs={"href": article_link})
        a.string = article_title

        return a

    def get_posts(self, root_content):
        if root_content is None:
            root_content = self.get_root_content()

        if not isinstance(root_content, Tag):
            root_content = BeautifulSoup(root_content, "lxml")

        if len(root_content.body) == 0:
            raise Exception("Empty body received")

        return root_content.select(".posts-main-gallery .row article")

    def get_top_article_a(self, root_content=None) -> Tag:
        posts = self.get_posts(root_content)

        return posts[0].select_one("a:has(> span.titleText)")

    def get_substories_a(self, root_content=None) -> list[Tag]:
        posts = self.get_posts(root_content)

        posts.pop(0)

        substories = []
        for article in posts:
            substories.append(article.select_one("a:has(> span.titleText)"))

        return substories

    def get_times(self, url, html=None):
        html, url = self.get_html(url, html)

        published_timestamp: str = html.select_one(self.published_selector).attrs["datetime"]
        last_updated = html.select_one(".single-post-meta-dates time:last-child").attrs["datetime"]
        last_updated = datetime.strptime(last_updated.strip(), "%Y-%m-%dT%H:%M:%S.000Z")
        published = datetime.strptime(published_timestamp.strip(), "%Y-%m-%dT%H:%M:%S.000Z")

        return published, last_updated
