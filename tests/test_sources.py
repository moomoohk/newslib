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


def test_source(source):
    root_content = source.get_root_content()

    top_article = source.get_top_article_a(root_content)
    assert isinstance(top_article, Tag)

    top_article_category = source.get_category(top_article.attrs["href"])
    assert isinstance(top_article_category, str)

    substories = source.get_substories_a(root_content)
    assert isinstance(substories, list)
