import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 523],
)
adapter = HTTPAdapter(max_retries=retry)
session = requests.Session()

session.mount('https://habr.com', adapter)
