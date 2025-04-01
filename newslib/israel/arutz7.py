import json
from datetime import datetime
from typing import Union

from bs4 import Tag

from newslib.source import Source


class Arutz7Source(Source):
    def __init__(self):
        super().__init__(
            name="arutz7",
            root="https://www.inn.co.il/api/NewAPI/HP",
            rss_news_link="https://www.inn.co.il/Rss.aspx?act=0.1",
            rss_news_flashes="https://www.inn.co.il/Rss.aspx",
        )

    @staticmethod
    def get_article_data(url):
        article_id = url.split("/")[-1]
        article_data_url = f"https://www.inn.co.il/api/NewAPI/Item?type=0&Item={article_id}&preview=0"

        data, _ = Source.get_content(article_data_url)
        data = json.loads(data)

        return data

    def get_root_content(self):
        root_content = super().get_root_content()
        return json.loads(root_content)

    def get_top_article_a(self, root_content: Union[str, bytes, Tag] = None) -> Tag:
        article_obj = root_content["data"]["Page"][0]["Items"][0]
        a = Tag(
            name="a",
            attrs={
                "href": article_obj["shotedLink"]
            }
        )
        a.string = f"{article_obj['title2']} {article_obj['short']}"

        return a

    def get_substories_a(self, root_content: Union[str, bytes, Tag] = None) -> list[Tag]:
        substories = root_content["data"]["Page"][0]["Items"][1:5]
        a_list = []
        for substory in substories:
            a = Tag(
                name="a",
                attrs={
                    "href": substory["shotedLink"]
                }
            )
            a.string = f"{substory['title2']} {substory['short']}"
            a_list.append(a)

        return a_list


    def valid_substory(self, a):
        return a.attrs["href"].lower().startswith("/news/")

    def get_category(self, url, html=None):
        data = self.get_article_data(url)
        return data["catname"]

    def get_times(self, url, html=None):
        data = self.get_article_data(url)
        return datetime.fromisoformat(data["itemDate"]), datetime.fromisoformat(data["firstUpdate"])

    @property
    def top_article_selector(self) -> str:
        return ""

    @property
    def substories_selector(self) -> str:
        return ""

    @property
    def category_selector(self) -> str:
        return ""

    @property
    def published_selector(self) -> str:
        return ""
