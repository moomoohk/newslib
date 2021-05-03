from datetime import datetime
from urllib.parse import urlparse

from newslib.source import Source


class HaaretzSource(Source):
    def __init__(self):
        super().__init__(
            name="haaretz",
            root="https://www.haaretz.co.il/news",
            rss_news_link="https://www.haaretz.co.il/cmlink/1.1470869",
            rss_tags_name="category",
            tags_selector="article > div > section > div > div > div > div > ul a",
        )

    @property
    def top_article_selector(self) -> str:
        return "article > div > div > a"

    @property
    def substories_selector(self) -> str:
        return "article > div > a:has(h2)"

    @property
    def category_selector(self) -> str:
        return "nav"

    @property
    def published_selector(self) -> str:
        return "time"

    def is_premium(self, url, html=None):
        return ".premium" in url

    def get_rss_item_tags(self, item):
        return [tag.text.strip() for tag in item.select(self.rss_tags_name)]

    def get_headline(self, a, top_article=False):
        if top_article:
            return a.select_one("h1").text

        return (a.select_one("h2 > span") or a.select_one("h2")).text

    def get_times(self, url, html=None):
        html = self.get_html(url, html)

        published = html.select_one(self.published_selector)
        if published.has_attr("datetime"):
            published = datetime.strptime(published.attrs["datetime"], "%Y-%m-%dT%H:%M:%S%z")

        return published, None

    def get_category(self, url, html=None):
        html = self.get_html(url, html)

        nav = html.select_one(self.category_selector)
        if nav is None:
            return None

        breadcrumbs = nav.select("span > a")

        if urlparse(url).path.startswith("/news/"):
            return breadcrumbs[1].text

        return breadcrumbs[0].text
