from pathlib import Path
from typing import Optional

import typer


def check_threads_cli_param(num_threads: int) -> Optional[int]:
    if num_threads < 1:
        raise typer.BadParameter('there must be at least 1 thread')
    return num_threads


def check_articles_cli_param(num_articles: int) -> Optional[int]:
    if num_articles < 1:
        raise typer.BadParameter('there must be at least 1 article to retrieve')
    return num_articles


def check_storage_path_exists(path_str: str) -> Optional[str]:
    if not Path(path_str).exists() and not Path(path_str).parent.exists():
        raise typer.BadParameter('path is invalid')
    return path_str
