from typing import Callable, Optional, Tuple
from urllib.parse import urljoin

import cloudscraper

from app.types import Comic, ProxyConfig, SearchItem


class Source:
    NAME = ""  # Name will be shown at anywhere this implementation used
    BASE_URL = ""  # base url for api or websitee

    def __init__(self):
        self.cs = cloudscraper.create_scraper(
            interpreter="js2py",  # Recommended for v3 challenges
            delay=5,  # Allow more time for complex challenges
        )

        pass

    def search(
        self, query: str, proxy_config: Optional[ProxyConfig]
    ) -> Tuple[Optional[list[SearchItem]], Optional[str]]:
        """
        Returns SearchItem list or error string
        """
        return None, "This function is not implemented in this source"

    def get(
        self, id: str, proxy_config: Optional[ProxyConfig]
    ) -> Tuple[Optional[Comic], Optional[str]]:
        """
        Returns Comic or error string
        """
        return None, "This function is not implemented in this source"

    def discover(
        self, proxy_config: Optional[ProxyConfig]
    ) -> Tuple[Optional[list[SearchItem]], Optional[str]]:
        """
        Returns SearchItem or error string
        """
        return None, "This function is not implemented in this source"

    def download(
        self, id: str, proxy_config: Optional[ProxyConfig], progress_callback: Callable
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Downloads given issue from source

        Args:
        id (str): id of issue at remote source.
            progress (Callable): callable to give to report download progress in percentage.

        Returns path to downloaded file, or error message
        """
        return None, "This function is not implemented in this source"

    def _make_request(
        self,
        path: str,
        method: str = "GET",
        params: dict = {},
        data: dict = {},
        headers: dict = {},
    ):

        url = urljoin(self.BASE_URL, path)

        if method.lower() == "get":
            return self.cs.get(url, params=params, data=data, headers=headers)
        elif method.lower() == "post":
            return self.cs.post(url, params=params, data=data, headers=headers)
        elif method.lower() == "put":
            return self.cs.put(url, params=params, data=data, headers=headers)
        elif method.lower() == "delete":
            return self.cs.delete(url, params=params, data=data, headers=headers)
        else:
            raise NotImplementedError(
                f"This request type is not implemented: {method}."
            )

    def _reinitialize_cloudscraper(self, proxy_config: Optional[ProxyConfig]):
        if proxy_config:
            proxies = {
                "http": proxy_config.build_url(),
                "https": proxy_config.build_url(),
            }

        self.cs.proxies = proxies
        self.cs.trust_env = False
