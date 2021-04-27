import logging
import shutil
from pathlib import Path
from queue import Queue
from threading import Thread

from bs4 import BeautifulSoup, Tag
from bs4.element import Comment, PageElement, ResultSet
from pathvalidate import sanitize_filename

from app.session import session

logger = logging.getLogger(__name__)


def check_if_tage_is_visible(element: PageElement) -> bool:
    if element.parent.name in [
        'style',
        'script',
        'head',
        'title',
        'meta',
        '[document]',
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def store_text_and_images(
    storage_path: Path, title: str, text: str, img_tags: ResultSet
) -> None:
    new_dir = storage_path / title
    new_dir.mkdir(exist_ok=True)

    filepath = new_dir / 'article.txt'
    with filepath.open('w', encoding='utf-8') as f:
        f.write(text)

    for image_num, tag in enumerate(img_tags, 1):
        logger.debug('Thread acquiring image %s', tag['src'])
        src = tag['src']
        response = session.get(src, stream=True)
        img_type = src.split('.')[-1]

        logger.debug('Thread saving that image')
        img_path = new_dir / f'image-{image_num}.{img_type}'
        with img_path.open('wb') as img:
            shutil.copyfileobj(response.raw, img)


def extract_title_and_text_from_article_tag(article_tag: Tag) -> tuple[str, str]:
    title_tag = article_tag.find(class_='post__title post__title_full')
    title_text = str(sanitize_filename(title_tag.text))
    visible_text_list = [
        text.strip()
        for text in article_tag.find_all(text=True)
        if check_if_tage_is_visible(text)
    ]
    visible_text = u' '.join(visible_text_list)

    return title_text, visible_text


def _parse_article(html_text: str) -> tuple[str, str, ResultSet]:
    logger.debug('Thread extracting text and images')
    soup = BeautifulSoup(html_text, 'html.parser')
    article_tag = soup.find('article', class_='post post_full')
    article_body_tag = article_tag.find('div', class_='post__body post__body_full')

    title, text = extract_title_and_text_from_article_tag(article_tag)
    img_tags = article_body_tag.findAll('img', {'src': True})

    return title, text, img_tags


def download_article(url: str, storage_path: Path) -> None:
    logger.debug('Thread sent request to %s', url)
    response = session.get(url)
    if response.status_code // 100 != 2:
        logger.critical(
            "Couldn't get response from habr.com - status code: %d",
            response.status_code,
        )

    title, text, img_tags = _parse_article(response.text)

    logger.debug('Thread saving text and images')
    store_text_and_images(storage_path, title=title, text=text, img_tags=img_tags)


class DownloadThread(Thread):
    def __init__(self, number: int, queue: Queue[tuple[Path, str]]) -> None:
        Thread.__init__(self)
        self.queue = queue
        self.number = number

    def run(self) -> None:
        while True:
            storage_path, link = self.queue.get()
            logger.info('Thread-%d started downloading %s', self.number, link)
            try:
                download_article(url=link, storage_path=storage_path)
            finally:
                self.queue.task_done()
            logger.info('Thread-%d finished downloading %s', self.number, link)
