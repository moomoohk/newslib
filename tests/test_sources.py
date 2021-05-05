from datetime import datetime
from urllib.parse import urljoin

from _pytest.python import Metafunc
from bs4.element import Tag

from newslib.israel.arutz7 import Arutz7Source
from newslib.israel.haaretz import HaaretzSource
from newslib.israel.israelhayom import IsraelHayomSource
from newslib.israel.maariv import MaarivSource
from newslib.israel.n12 import N12Source
from newslib.israel.news0404 import News0404Source
from newslib.israel.news13 import News13Source
from newslib.israel.walla import WallaSource
from newslib.israel.ynet import YnetSource
from newslib.source import Source


def pytest_generate_tests(metafunc: Metafunc):
    sources = [
        Arutz7Source(),
        HaaretzSource(),
        IsraelHayomSource(),
        MaarivSource(),
        N12Source(),
        News13Source(),
        News0404Source(),
        WallaSource(),
        YnetSource(),
    ]
    metafunc.parametrize("source", sources, ids=[source.name for source in sources])


def test_source(source: Source):
    root_content = source.get_root_content()

    top_article_a = source.get_top_article_a(root_content)
    assert isinstance(top_article_a, Tag)

    top_article_url = urljoin(source.root, top_article_a.attrs["href"])
    top_article_html = source.get_html(top_article_url)

    top_article_headline = source.get_headline(top_article_a, top_article=True)
    assert isinstance(top_article_headline, str)

    top_article_category = source.get_category(top_article_url, top_article_html)
    assert isinstance(top_article_category, str)

    top_article_tags = source.get_tags(top_article_url, top_article_html)
    if source.tags_selector is None:
        assert top_article_tags is None
    else:
        assert isinstance(top_article_tags, list)
        if len(top_article_tags) > 0:
            assert all([isinstance(tag, str) for tag in top_article_tags])

    top_article_created, top_article_updated = source.get_times(top_article_url, top_article_html)
    assert isinstance(top_article_created, datetime)
    if top_article_updated is not None:
        assert isinstance(top_article_updated, datetime)

    substories_a = source.get_substories_a(root_content)
    assert isinstance(substories_a, list)

    first_substory_a = substories_a[0]

    substory_headline = source.get_headline(first_substory_a)
    assert isinstance(substory_headline, str)

    assert isinstance(source.valid_substory(first_substory_a), bool)
