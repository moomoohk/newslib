from distutils.core import setup

from setuptools import find_packages

setup(
    name="newslib",
    version="0.2",
    packages=find_packages(),
    url="",
    license="",
    author="moomoohk",
    author_email="",
    description="newslib",
    install_requires=[
        "beautifulsoup4",
        "pytest",
        "requests",
        "lxml",
        "lzstring",
    ]
)
