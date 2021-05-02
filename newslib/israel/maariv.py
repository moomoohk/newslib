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
        return ".top-story-text-wrap > a"

    @property
    def substories_selector(self) -> str:
        return ".three-articles-in-row > a"

    @property
    def category_selector(self) -> str:
        return ".article-breadcrumbs > ul > li:last-child > a"

    @property
    def published_selector(self) -> str:
        return ".article-publish-date"

    def extract_headline(self, a, top_article=False):
        if top_article:
            return a.select_one(".top-story-title").text

        return a.select_one(".three-articles-in-row-title").text

    def get_times(self, html, link):
        article_metadatas = html.select(self.json_metadata_selector)

        for metadata_tag in article_metadatas:
            metadata = loads(metadata_tag.string.strip().replace("\r\n", "").replace("&quot;", "\\\""))

            if "@type" in metadata and metadata["@type"] == "NewsArticle":
                datetime_format = "%Y-%m-%dT%H:%MZ"
                published = datetime.strptime(metadata["datePublished"], datetime_format)
                modified = datetime.strptime(metadata["dateModified"], datetime_format)

                return published, modified

        raise Exception(f"Couldn't get times for {link}")

    def get_category(self, html, link):
        if urlparse(link).netloc.startswith("sport1."):
            return "ספורט"

        return super().get_category(html, link)
