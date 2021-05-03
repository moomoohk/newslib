from datetime import datetime

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

    @property
    def top_article_selector(self) -> str:
        return "section.top-section > a"

    @property
    def substories_selector(self) -> str:
        return "#container > section.fc.common-section.grid-1-2 > section > " \
               "section.sequence.common-articles.editor-selections.no-title > ul > li > article > a "

    @property
    def category_selector(self) -> str:
        return "nav.breadcrumb > ul > li"

    @property
    def published_selector(self) -> str:
        return "time"

    def get_headline(self, a, top_article=False):
        return a.select_one("h3").text.strip()

    def get_times(self, url, html=None):
        html = self.get_html(url, html)

        published = html.select_one(self.published_selector)
        if published.has_attr("datetime"):
            published = datetime.strptime(published.attrs["datetime"], "%Y-%m-%d %H:%M")

        return published, None

    def get_category(self, url, html=None):
        html = self.get_html(url, html)

        nav = html.select_one(self.category_selector)

        if nav.text == "חדשות" and nav.next_sibling is not None:
            return nav.next_sibling.text.strip()

        return nav.text.strip()
