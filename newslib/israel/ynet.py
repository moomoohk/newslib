from datetime import datetime
from unicodedata import normalize

from bs4 import BeautifulSoup

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
        self.updated_selector = "div.art_header_footer > span:nth-child(3), div.authorAndDateContainer div.date"
        self.find_error_selector = "#find_error"

    @property
    def top_article_selector(self) -> str:
        return ".TopStoryComponenta .slotTitle > a"

    @property
    def substories_selector(self) -> str:
        return ".strip-1150 .textDiv a"

    @property
    def category_selector(self) -> str:
        return "ul.trj_trajectory, nav.categoryBreadcrumbs > ul"

    @property
    def published_selector(self) -> str:
        return "div.originalLaunchDate"

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

    def is_premium(self, url, html=None):
        html = self.get_html(url, html)

        return html.select_one(self.premium_selector) is not None

    def get_category(self, url, html=None):
        html = self.get_html(url, html)

        breadcrumbs = html.select_one(self.category_selector)

        if breadcrumbs is None:
            breadcrumbs = html.select_one("nav.categoryBreadcrumbs")

        first_breadcrumb = breadcrumbs.select_one("li:first-child")

        if first_breadcrumb.text in ["חדשות"]:
            if first_breadcrumb.next_sibling.text == "פרשנות וטורים":
                return first_breadcrumb.next_sibling.text

            return list(breadcrumbs.children)[-1].text

        return first_breadcrumb.text

    def get_times(self, url, html=None):
        html = self.get_html(url, html)

        published_text: str = normalize("NFKD", html.select_one(self.updated_selector).text)
        last_updated = None
        published = None

        originally_published = html.select_one(self.published_selector)
        if originally_published is None:
            find_error = html.select_one(self.find_error_selector)

            if find_error is not None:
                originally_published = find_error.find_previous()

        if originally_published is not None and len(originally_published) > 0:
            originally_published_text = normalize("NFKD", originally_published.text)
            originally_published_text = originally_published_text.split(" ", 2)[-1].strip()

            if "," in originally_published_text:
                published = datetime.strptime(originally_published_text, "%H:%M , %d.%m.%y")
            else:
                published = datetime.strptime(originally_published_text, "%d/%m/%Y %H:%M")

        date_type, date_text = published_text.split(":", 1)

        if "פורסם" in date_type:
            published = datetime.strptime(date_text.strip(), "%d.%m.%y , %H:%M")
        elif "עודכן" in date_type or "עדכון" in date_type:
            last_updated = datetime.strptime(date_text.strip(), "%d.%m.%y , %H:%M")

        return published, last_updated
