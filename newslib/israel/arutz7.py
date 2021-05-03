from datetime import datetime
from unicodedata import normalize

from newslib.source import Source


class Arutz7Source(Source):
    def __init__(self):
        super().__init__(
            name="arutz7",
            root="https://www.inn.co.il/",
            rss_news_link="https://www.inn.co.il/Rss.aspx?act=0.1",
            rss_news_flashes="https://www.inn.co.il/Rss.aspx",
        )

    def valid_substory(self, a):
        return a.attrs["href"].startswith("/News/")

    def get_headline(self, a, top_article=False):
        if top_article:
            return a.select_one("strong").text.strip()

        return a.select_one("h2").text.strip()

    def get_category(self, url, html=None):
        html = self.get_html(url, html)

        breadcrumbs = html.select_one(self.category_selector)

        return breadcrumbs.select("a")[2].text

    def get_times(self, url, html=None):
        html = self.get_html(url, html)

        published_text: str = normalize("NFKD", html.select_one(self.published_selector).text)
        published = datetime.strptime(published_text, "%d/%m/%y %H:%M")

        return published, None

    @property
    def top_article_selector(self) -> str:
        return "#HPMain a.HPTLink"

    @property
    def substories_selector(self) -> str:
        return "#main > div.HPTitles.HPTitles1 a.HPTLink"

    @property
    def category_selector(self) -> str:
        return "#BreadCrumbs"

    @property
    def published_selector(self) -> str:
        return "span[itemprop='datePublished']"
