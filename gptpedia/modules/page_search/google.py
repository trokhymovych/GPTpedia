import copy
import logging
import re
import time
import urllib

from typing import Any

import pandas as pd
import requests

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from gptpedia.modules.constants import DEFAULT_SEARCH_SCORE
from gptpedia.modules.entities import PageSearchResult
from gptpedia.modules.page_search.wiki import PageSearchBase


logger = logging.getLogger(__name__)


class PageSearchGoogle(PageSearchBase):
    def __init__(self, logger_object: logging.Logger = logger, **kwargs: Any):
        super().__init__(logger_object, **kwargs)

    def search(self, query: str, **kwargs) -> PageSearchResult:
        proxy_dict = kwargs.get("proxy_dict")
        site_modifier = kwargs.get("site_modifier")

        if site_modifier:
            query += f" site:{site_modifier}"

        tld = 'com'
        lang = 'en'

        query_processed = urllib.parse.quote_plus(query)  # Format into URL encoding

        ua = UserAgent()
        google_url = f"http://www.google.{tld}/search?lr=lang_{lang}&" \
                     f"q={query_processed}"
        if proxy_dict:
            response = requests.get(google_url, {"User-Agent": ua.random}, proxies=proxy_dict, timeout=5, verify=False)
        else:
            response = requests.get(google_url, {"User-Agent": ua.random}, timeout=5, verify=False)

        soup = BeautifulSoup(response.text, "html.parser")
        result = soup.find_all('div', attrs={'class': 'egMi0 kCrYT'})
        results = [re.search("\/url\?q\=(.*)\&sa", str(i.find('a', href=True)['href'])) for i in result if
                   "url" in str(i)]
        links = [i.group(1) for i in results if i is not None]

        # todo: Add names extractions if needed.
        search_result = PageSearchResult(
            query=query,
            n_results=len(links),
            pages_names=links,
            scores=[DEFAULT_SEARCH_SCORE],
            pages_links=links
        )
        return search_result

    def _check_proxy(self, px):
        ua = UserAgent()
        try:
            google_url = "http://www.google.com/search?q=" + "machine+learning" + "&num=" + str(10)
            a = requests.get(google_url, {"User-Agent": ua.random}, proxies={"http": "http://" + px}, timeout=5)
            if a.status_code == 429:
                return False
        except Exception as e:
            self.logger.info(f"Proxy {px} is not valid. {e}")
            return False
        return True

    def get_proxy(self, old_proxy="", checked_proxies=[]):
        self.logger.info("Getting new proxy....")
        # Todo: consider different sources.
        html = requests.get("https://free-proxy-list.net/").content
        df_proxy = pd.read_html(html)[0]
        df_proxy = df_proxy[(df_proxy.Google == "yes")]
        df_proxy = df_proxy[(df_proxy.Google != "no")]
        df_proxy["proxy_str"] = df_proxy.apply(lambda row: str(row[0]) + ":" + str(row[1]), axis=1)

        current_checked_proxies = copy.deepcopy(checked_proxies)
        current_checked_proxies.append(old_proxy)
        for p in df_proxy.proxy_str.values:
            if (p not in current_checked_proxies) & self._check_proxy(p):
                return p
            current_checked_proxies.append(p)
        self.logger.info("Unable to find new proxy, waiting 10 seconds....")
        time.sleep(10)
        return self.get_proxy(old_proxy, current_checked_proxies)


# ## Sample usage with proxy:
# wiki_search = GoogleSearchWiki()
#
# # getting the proxy:
# proxy_string = wiki_search.get_proxy()
# proxy_dict = {"http" : f"http://{proxy_string}"}
#
# # search:
# query = "The Earth is flat."
# try:
#     # Trying to get the results. In case the process fails, we should implement the custom handling logic
#     # The most likely reason is google blocking the scraping, so change of proxy is needed.
#     search_results = wiki_search.search(query, proxy_dict=proxy_dict)
# except:
#     # Handling logic goes here.
#     pass
