from pathlib import Path
from typing import List

import pytest

from app.main import app


def get_article_text(path: Path, article_num: int) -> List[str]:
    article_folder = path / f'Title{article_num}'
    with open(article_folder / 'article.txt') as f:
        article_text = f.read().split()

    return article_text


def get_article_images(path: Path, article_num: int) -> List[bytes]:
    article_folder = path / f'Title{article_num}'

    images = []
    for filename in article_folder.iterdir():
        if 'image' in str(filename):
            with open(filename, 'rb') as img:
                images.append(img.read())

    return images


@pytest.mark.parametrize(
    ('num_of_articles',),
    [
        (1,),
        (2,),
        (3,),
        (4,),
    ],
)
@pytest.mark.usefixtures('mocker')
def test_correct_args(runner, num_of_articles, expected_results, tmp_path):
    folder_name = str(tmp_path.absolute())
    response = runner.invoke(
        app, ['-t', '2', '-a', num_of_articles, '-sp', folder_name]
    )

    for article_index in range(1, num_of_articles + 1):
        text = get_article_text(Path(folder_name), article_index)
        images = set(get_article_images(Path(folder_name), article_index))
        expected_text = expected_results[article_index - 1][0]
        expected_images = set(expected_results[article_index - 1][1])

        assert text == expected_text
        assert images == expected_images

    assert response.exit_code == 0


@pytest.mark.parametrize(
    ('num_of_articles', 'num_of_threads', 'storage_path'),
    [
        ('invalid', 1, './for_testing'),
        (1, 'invalid', './for_testing'),
        (0, 1, './for_testing'),
        (1, 0, './for_testing'),
        (1, 1, '/some/non/existing/path'),
    ],
)
def test_incorrect_args(runner, num_of_articles, num_of_threads, storage_path):
    response = runner.invoke(
        app, ['-t', num_of_threads, '-a', num_of_articles, '-sp', storage_path]
    )

    assert response.exit_code != 0
