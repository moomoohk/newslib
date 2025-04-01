from datetime import datetime
from unicodedata import normalize

from newslib.source import Source


class News0404Source(Source):
    def __init__(self):
        super().__init__(
            name="0404",
            root="https://www.0404.co.il/",
            rss_news_link="https://www.0404.co.il/?call_custom_simple_rss=1&csrp_cat=1",
            rss_news_flashes="https://www.0404.co.il/?call_custom_simple_rss=1&csrp_cat=14",
            rss_datetime_format="%Y-%m-%d %H:%M:%S",
            rss_created_tag="dc:created",
            rss_modified_tag="dc:modified",
            include_query_string=True,
        )

    @property
    def top_article_selector(self) -> str:
        return "div.topcategory > ul > li:nth-child(1) .topcattext h4 a"

    @property
    def substories_selector(self) -> str:
        return "div.topcategory > ul > li:not(:nth-child(1)) .topcattext h4 a"

    @property
    def category_selector(self) -> str:
        return "#main_container > div.wrap > div.single_content.desktop > div > div.right_content > div.breadcrumbs" \
               " > span:nth-child(2) > a > span"

    @property
    def published_selector(self) -> str:
        return "#main_container > div.wrap > div.single_content.desktop > div > div.right_content > " \
               "div.article_section > div.post_meta.cf > div.post_date"

    def get_times(self, url, html=None):
        html, url = self.get_html(url, html)
        
        published_text: str = normalize("NFKD", html.select_one(self.published_selector).text)
        last_updated = None
        published = datetime.strptime(published_text.strip(), "%d/%m/%Y %H:%M")

        return published, last_updated
