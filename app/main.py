import logging
import time
from pathlib import Path
from queue import Queue
from typing import List, Optional, Tuple

import typer
from bs4 import BeautifulSoup, ResultSet

from app.session import session
from app.validators import (
    check_articles_cli_param,
    check_storage_path_exists,
    check_threads_cli_param,
)
from app.workers import DownloadThread

logger = logging.getLogger(__name__)
app = typer.Typer()


def make_storage_folder(path: Path) -> Path:
    try:
        path.mkdir(exist_ok=True)
    except FileNotFoundError as e:
        raise typer.BadParameter(f'No such file or directory: {path}') from e

    return path


def _get_article_tag_from_html(html_text: str) -> Optional[ResultSet]:
    soup = BeautifulSoup(html_text, 'html.parser')
    posts_list = soup.find('div', class_='posts_list')
    return posts_list.find_all('article', class_='post post_preview')


def _get_article_tag_from_url(url: str) -> Optional[ResultSet]:
    response = session.get(url)

    if response.status_code // 100 != 2:
        logger.critical(
            "Couldn't get response from habr.com - status code: %d",
            response.status_code,
        )
        return None

    return _get_article_tag_from_html(response.text)


def get_articles_links(amount: int = 25) -> list[str]:
    page_num = 1
    is_finished = False
    links = []
    logger.info("Starting Collecting Articles' Links")
    while not is_finished:
        articles = _get_article_tag_from_url(f'https://habr.com/ru/page{page_num}/')
        page_num += 1
        if not articles:
            break

        for article in articles:
            anchor = article.find('a', class_='post__title_link')

            links.append(anchor['href'])

            logger.info('%s', anchor)
            logger.info('LINKS OBTAINED = %d / %d', len(links), amount)

            if len(links) >= amount:
                is_finished = True
                break

    logger.info("Finished Collecting Articles' Links")

    return links


def start_working_threads(
    num_threads: int,
    storage_folder: Path,
    article_links: List[str],
    queue: Queue[Tuple[Path, str]],
) -> None:
    logger.info('Started Initialization Of Threads')
    for thread_num in range(num_threads):
        thread = DownloadThread(thread_num, queue)
        thread.daemon = True
        thread.start()

    for link in article_links:
        logger.info('Queueing: %s', link)
        queue.put((storage_folder, link))


@app.command()
def main(
    num_threads: int = typer.Option(
        3,
        '--threads',
        '-t',
        help='The number of working threads',
        callback=check_threads_cli_param,
    ),
    num_articles_to_retrieve: int = typer.Option(
        5,
        '--articles',
        '-a',
        help='The number of articles to download',
        callback=check_articles_cli_param,
    ),
    storage_path: Path = typer.Option(
        Path('./habr_articles'),
        '--storage-path',
        '-sp',
        help='Dir to folder in which articles will be stored',
        callback=check_storage_path_exists,
    ),
) -> None:
    """
    Download the most recent articles from habr.com
    """
    start_time = time.time()

    storage_folder = make_storage_folder(storage_path)
    article_links = get_articles_links(amount=num_articles_to_retrieve)
    queue: Queue[Tuple[Path, str]] = Queue()

    with typer.progressbar(
        range(-1, num_articles_to_retrieve), label='Downloading', show_eta=False
    ) as progress:
        start_working_threads(
            num_threads=num_threads,
            storage_folder=storage_folder,
            article_links=article_links,
            queue=queue,
        )

        for p in progress:
            to_download = num_articles_to_retrieve - p
            while to_download == queue.qsize():
                time.sleep(1)

    queue.join()

    end_time = time.time()
    logger.info('Completed in: %f seconds', (end_time - start_time))


if __name__ == '__main__':
    app()
