from pathlib import Path

import pytest
import requests_mock
from typer.testing import CliRunner

# pylint: disable=(redefined-outer-name)


@pytest.fixture()
def runner():
    yield CliRunner()


@pytest.fixture()
def main_pages_content():
    return [
        Path('tests/pages/main/page_1.html').read_text(),
        Path('tests/pages/main/page_2.html').read_text(),
    ]


@pytest.fixture()
def articles_content():
    return [
        Path('tests/pages/articles/article1.html').read_text(),
        Path('tests/pages/articles/article2.html').read_text(),
        Path('tests/pages/articles/article3.html').read_text(),
        Path('tests/pages/articles/article4.html').read_text(),
    ]


@pytest.fixture()
def images_content():
    return [
        Path('tests/images/image1.jpg').read_bytes(),
        Path('tests/images/image2.jpg').read_bytes(),
        Path('tests/images/image3.jpg').read_bytes(),
        Path('tests/images/image4.jpg').read_bytes(),
        Path('tests/images/image5.jpg').read_bytes(),
    ]


@pytest.fixture()
def empty_mocker():
    with requests_mock.Mocker() as rm:
        yield rm


def register_main_pages(cur_mocker, main_pages_content):
    for page_num, page_content in enumerate(main_pages_content, 1):
        cur_mocker.get(f'https://habr.com/ru/page{page_num}/', text=page_content)


def register_articles(cur_mocker, articles_content):
    for page_num, page_content in enumerate(articles_content, 1):
        cur_mocker.get(f'https://habr.com/ru/post/{page_num}/', text=page_content)


def register_images(cur_mocker, images_content):
    for page_num, page_content in enumerate(images_content, 1):
        cur_mocker.get(
            f'https://habrastorage.org/images/image{page_num}.jpg', content=page_content
        )


@pytest.fixture()
def mocker(empty_mocker, articles_content, main_pages_content, images_content):
    register_articles(empty_mocker, articles_content)
    register_main_pages(empty_mocker, main_pages_content)
    register_images(empty_mocker, images_content)
    return empty_mocker


@pytest.fixture()
def article1_expected_result(images_content):
    text = ['Title1', 'Text1', 'Text2', 'Text3', 'Text4', 'Text5']
    images = images_content[:2]
    return text, images


@pytest.fixture()
def article2_expected_result(images_content):
    text = ['Title2', 'Text6', 'Text7', 'Text8']
    images = images_content[2:]
    return text, images


@pytest.fixture()
def article3_expected_result():
    text = ['Title3', 'Text9', 'Text10', 'Text11']
    return text, []


@pytest.fixture()
def article4_expected_result(images_content):
    text = ['Title4', 'Text']
    images = [images_content[3]]
    return text, images


@pytest.fixture()
def expected_results(
    article1_expected_result,
    article2_expected_result,
    article3_expected_result,
    article4_expected_result,
):
    return [
        article1_expected_result,
        article2_expected_result,
        article3_expected_result,
        article4_expected_result,
    ]
