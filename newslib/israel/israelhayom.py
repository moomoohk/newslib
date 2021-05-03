from datetime import datetime

from newslib.source import Source


# Requires JS...
class IsraelHayomSource(Source):
    def __init__(self):
        super().__init__(
            name="israelhayom",
            root="https://www.israelhayom.co.il/",
            rss_news_link="https://www.israelhayom.co.il/rss.xml",
            tags_selector=".tags-list > li:not(.first) > a",
        )

    @property
    def top_article_selector(self) -> str:
        return "#block-system-main > div > div.panel-panel.line.top.clearfix.mquery-hp-1 > div > div.top-wide > " \
               "div.panel-pane.pane-ih-main-lobby-topstory > div > div > div.wrapper-top > section > article " \
               ".content-second > a "

    @property
    def substories_selector(self) -> str:
        return ".line.top .top-wide > .pane-ih-main-lobby-topstory > div > div > .wrapper-bottom .item-sub-article > " \
               "article > div > a "

    @property
    def category_selector(self) -> str:
        return ".field-section-breadcrumb .last"

    @property
    def published_selector(self) -> str:
        return ".time time"

    def get_times(self, url, html=None):
        html = self.get_html(url, html)

        published_timestamp: str = html.select_one(self.published_selector).attrs["datetime"]
        last_updated = None
        published = datetime.strptime(published_timestamp.strip(), "%Y-%m-%dT%H:%M:%S")

        return published, last_updated

    def get_headline(self, a, top_article=False):
        if top_article:
            return a.select_one(".title").text.strip()

        return a.select_one(".teaser-title").text.strip()
