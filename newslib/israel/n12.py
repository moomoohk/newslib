from datetime import datetime

from newslib.source import Source


class N12Source(Source):
    def __init__(self):
        super().__init__(
            name="n12",
            root="https://www.n12.co.il/",
        )

    @property
    def top_article_selector(self) -> str:
        return "#part1 > .grid-ordering.main1 > li:first-child strong > a"

    @property
    def substories_selector(self) -> str:
        return "#part1 > .grid-ordering.main1 > li:not(:first-child) strong > a"

    @property
    def category_selector(self) -> str:
        return "nav.breadcrumbs-v_2017 ul > li"

    @property
    def published_selector(self) -> str:
        return ".writer-data > span.display-date"

    def get_times(self, url, html=None):
        html, url = self.get_html(url, html)

        published = html.select_one(self.published_selector)

        spans = [span.text for span in published.find_all("span")]

        published = " ".join([spans[0], spans[1]]).replace("|", "").replace("פורסם", "").strip()
        published = datetime.strptime(published, "%d/%m/%y %H:%M")

        updated = published
        if len(spans) == 4:
            updated = " ".join([spans[2], spans[3]]).replace("|", "").replace("עודכן", "").strip()
            updated = datetime.strptime(updated, "%d/%m/%y %H:%M")

        return published, updated

    def get_category(self, url, html=None):
        html, url = self.get_html(url, html)

        category = html.select_one(self.category_selector)

        if category.text == "החדשות":
            category = category.next_sibling.next_sibling

        return category.text
