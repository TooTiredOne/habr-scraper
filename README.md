# Web Scraper

### Description:
    multithread scraper for downloading the most resent articles from habr.com

### Create venv:
    make venv

### Run tests:
    make test

### Run linters:
    make lint

### Run formatters:
    make format


### Run scraper
    After creating and activating the virtual env, you can run "scraper" command

```
$ scraper -- help

Usage: scraper [OPTIONS]

  Download the most recent articles from habr.com

Options:
  -t, --threads INTEGER     The number of working threads  [default: 3]
  -a, --articles INTEGER    The number of articles to download  [default: 5]
  -sp, --storage-path PATH  Dir to folder in which articles will be stored
                            [default: habr_articles]

  --install-completion      Install completion for the current shell.
  --show-completion         Show completion for the current shell, to copy it
                            or customize the installation.

  --help                    Show this message and exit.

``` 
