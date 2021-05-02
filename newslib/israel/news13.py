from datetime import datetime


from newslib.source import Source


# Requires JS...
class News13Source(Source):
    def __init__(self):
        super().__init__(
            name="news13",
            root="https://13news.co.il/",
        )

    @property
    def top_article_selector(self) -> str:
        return ".about-five-group-items .about-block-wrp .titleComp a"

    @property
    def substories_selector(self) -> str:
        return ".about-five-group-items .four-group-ul a"

    @property
    def category_selector(self) -> str:
        return ".breadCrumbs_2"

    @property
    def published_selector(self) -> str:
        return "time"

    def get_times(self, html, link):
        published_timestamp: str = html.select_one(self.published_selector).attrs["datetime"]
        last_updated = None
        published = datetime.strptime(published_timestamp.strip(), "%d/%m/%Y %H:%M")

        return published, last_updated
