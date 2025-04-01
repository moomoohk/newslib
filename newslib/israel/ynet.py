import ast
import json
import re
from datetime import datetime
from functools import lru_cache
from unicodedata import normalize

from bs4 import BeautifulSoup, Tag

from newslib.source import Source


class YnetSource(Source):
    def __init__(self):
        super().__init__(
            name="ynet",
            root="https://www.ynet.co.il/",
            rss_news_link="http://www.ynet.co.il/Integration/StoryRss2.xml",
            rss_news_flashes="http://www.ynet.co.il/Integration/StoryRss1854.xml",
            tags_selector="#articletags > a",
        )

        self.premium_selector = "#ynet_premium_blocked"
        # self.updated_selector = "div.art_header_footer > span:nth-child(3), div.authorAndDateContainer span.date"
        # self.find_error_selector = "#find_error"
        self.top_article_selectors = [
            ".TopStoryWideComponenta",
            ".TopStoryComponenta",
            ".TopStoryWarComponenta",
            ".TopStory1280Componenta"
        ]

        self.data_query_re = re.compile(r"dataLayer = \[(?P<data>.+?)\];", flags=re.DOTALL)

    def get_top_article_a(self, root_content=None):
        if root_content is None:
            root_content = self.get_root_content()

        if not isinstance(root_content, Tag):
            root_content = BeautifulSoup(root_content, "lxml")

        for top_article_selector in self.top_article_selectors:
            if (top_article_div := root_content.select_one(top_article_selector)) is not None:
                top_article_a = top_article_div.select_one("a")

                if top_article_a is not None:
                    return top_article_a

        raise Exception("Could not find top article")

    @property
    def substories_selector(self) -> str:
        return ".YnetMultiStripRowsComponenta .textDiv a"

    def check_rss_error(self, feed: BeautifulSoup):
        error = feed.find(id="lblCase")

        if error:
            raise Exception(f"Blocked. Case number {error.text}")

    def get_headline(self, a, top_article=False):
        title_div = a.select_one(".title")
        if title_div:
            headline_text = title_div.text.strip()
        else:
            headline_text = a.text.strip()

        return headline_text

    def valid_substory(self, a):
        href = a.attrs["href"]
        return "/fashion/" not in href and "/parents/" not in href and "/blogs/" not in href

    def is_premium(self, url, html=None):
        html, url = self.get_html(url, html)

        return html.select_one(self.premium_selector) is not None

    def get_category(self, url, html=None):
        html, url = self.get_html(url, html)

        category_meta = html.find("meta", attrs={"property": "sub-channel-name"})

        if category_meta is None:
            raise Exception("Could not find category meta tag")

        return category_meta.attrs["content"].split("/")[-1]

    def get_times(self, url, html=None):
        html, url = self.get_html(url, html)

        data = self.get_data(str(html))
        published_text: str = data["datePublished"]
        updated_text: str = data["dateModified"]

        published = datetime.strptime(published_text, "%Y-%m-%d %H:%M:%S")
        last_updated = None

        if updated_text != published_text:
            last_updated = datetime.strptime(updated_text, "%Y-%m-%d %H:%M:%S")

        return published, last_updated

    @lru_cache(maxsize=10)
    def get_data(self, html: str):
        match = re.search(self.data_query_re, html)
        if not match:
            raise Exception("Couldn't extract article data")

        data_text = re.sub(
            "'userId': window\.YitPaywall && YitPaywall\.user && YitPaywall\.user\.props \? YitPaywall\.user\.props\.userId : \'\'.+?,",
            "",
            match["data"],
            flags=re.DOTALL,
        )

        data_text = re.sub(
            "\'piano_id\': window\.YitPaywall && YitPaywall\.user && YitPaywall\.user\.props \? YitPaywall\.user\.props\.piano_id : \'\'.+?,",
            "",
            data_text,
            flags=re.DOTALL,
        )

        data_text = re.sub(
            "\'display\': window\.matchMedia\(\'\(prefers-color-scheme: dark\)\'\)\.matches \? \'dark_mode\' : \'light_mode\'.+?,",
            "",
            data_text,
            flags=re.DOTALL,
        )

        return ast.literal_eval(data_text)
