from datetime import datetime
from json import loads
from urllib.parse import urlparse

from newslib.source import Source


class MaarivSource(Source):
    def __init__(self):
        super().__init__(
            name="maariv",
            root="https://www.maariv.co.il/",
            rss_news_link="https://www.maariv.co.il/Rss/RssChadashot",
            rss_news_flashes="https://www.maariv.co.il/Rss/RssFeedsMivzakiChadashot",
            rss_guid="itemID",
            rss_tags_name="Tags",
            rss_datetime_format="%a, %d %b %Y %H:%M:%S %Z",
            rss_modified_tag="UpdateDate",
            tags_selector=".article-tags > ul > li > a",
        )

        self.json_metadata_selector = "head > script[type='application/ld+json']"
        self.article_metadata_index = 1

    @property
    def top_article_selector(self) -> str:
        return ".top-story-img-big > a"

    @property
    def substories_selector(self) -> str:
        return ".three-articles-in-row > a"

    @property
    def category_selector(self) -> str:
        return ".article-breadcrumbs > ul > li:last-child > a"

    @property
    def published_selector(self) -> str:
        return ".article-publish-date"

    def get_headline(self, a, top_article=False):
        if top_article:
            html, _ = self.get_html(self.root + a.attrs["href"])
            title = html.select_one("section.article-title").text.strip()
            return title

        return a.select_one(".three-articles-in-row-title").text.strip()

    def get_times(self, url, html=None):
        html, url = self.get_html(url, html)

        article_metadatas = html.select(self.json_metadata_selector)

        for metadata_tag in article_metadatas:
            metadata = loads(metadata_tag.string.strip().replace("\r\n", "").replace("&quot;", "\\\""))

            if "@type" in metadata and metadata["@type"] == "NewsArticle":
                published = datetime.fromisoformat(metadata["datePublished"])
                modified = datetime.fromisoformat(metadata["dateModified"])

                return published, modified

        raise Exception(f"Couldn't get times for {url}")

    def get_category(self, url, html=None):
        html, url = self.get_html(url, html)

        if urlparse(url).netloc.startswith("sport1."):
            return "ספורט"

        return super().get_category(url, html)

    def valid_substory(self, a) -> bool:
        href = a.attrs["href"]
        return "sport1.maariv.co.il" not in href

