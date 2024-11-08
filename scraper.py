from requests_html import AsyncHTMLSession
from collections import defaultdict
from collections import Counter
import urllib.parse
import os
import time
from tqdm import tqdm
import json
import logging


logger = logging.getLogger(__name__)

logging.basicConfig(filename="output.log", level=logging.DEBUG)

CHUNK_SIZE = 100


class WebScrapper:

    def __init__(
        self,
        urls,
        max_depth=1,
        black_list=[".jpg", ".png", ".jpeg", ".pdf", ".php"],
        save_html=False,
    ):
        self.urls = urls
        self.session = AsyncHTMLSession()
        self.max_depth = max_depth
        self.black_list = black_list
        self.page_structure = {}
        self.save_html = save_html

        for url in urls:
            self.page_structure[url] = defaultdict(dict)
            self.page_structure[url]["url_parse"] = urllib.parse.urlparse(url)
            self.page_structure[url]["visited"] = set()
            self.page_structure[url]["depth"] = 0
            self.page_structure[url]["statistics"] = Counter()
            self.page_structure[url]["results"] = {}
            self.page_structure[url]["time"] = -1

    async def get_html(self, url):
        # TODO: add auth, headers, cookies, proxies support
        response = await self.session.get(url)
        return response

    def get_responses(self, urls):
        def chunks(items, n):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(items), n):
                yield items[i : i + n]

        logger.info(f"Getting responses for a total of {len(urls)} urls")

        results = []

        for urls_chunk in tqdm(chunks(urls, CHUNK_SIZE), total=len(urls) // CHUNK_SIZE):
            results.extend(
                self.session.run(
                    *[lambda url=url: self.get_html(url) for url in urls_chunk]
                )
            )

        return results

    def store_html(self, folder, response):
        if not os.path.exists(f"./html_pages/{folder}"):
            os.makedirs(f"./html_pages/{folder}")
        netloc_name = urllib.parse.urlparse(response.url).netloc.replace(".", "_")
        path_name = urllib.parse.urlparse(response.url).path.replace("/", "_")
        with open(f"./html_pages/{folder}/{netloc_name}__{path_name}.html", "w") as f:
            # TODO: support on different types of encoding
            f.write(response.content.decode())

    def process(self, url):
        start = time.time()
        folder = self.page_structure[url]["url_parse"].netloc.replace(".", "_")
        urls = [url]
        while self.page_structure[url]["depth"] < self.max_depth and urls:
            logger.info(
                f'Processing {len(urls)} urls at depth {self.page_structure[url]["depth"]}'
            )

            self.page_structure[url]["depth"] += 1
            self.page_structure[url]["visited"] = self.page_structure[url][
                "visited"
            ].union(set(urls))
            results = self.get_responses(urls)
            urls = []
            for r in tqdm(results, total=len(results)):
                if self.save_html:
                    self.store_html(folder, r)

                self.page_structure[url]["statistics"][r.status_code] += 1
                self.page_structure[url]["results"][r.url] = {
                    "title": (
                        r.html.find("title")[0].text if r.html.find("title") else None
                    ),
                    "status_code": r.status_code,
                    "bytes": len(r.content),
                }
                urls += [link for link in r.html.absolute_links]
                logger.info(f"Number of new links {len(urls)}")
                urls = list(set(urls) - self.page_structure[url]["visited"])
                logger.info(f"Number of new links not visited {len(urls)}")
                urls = list(
                    filter(
                        lambda x: urllib.parse.urlparse(x).netloc
                        == self.page_structure[url]["url_parse"].netloc,
                        urls,
                    )
                )
                logger.info(f"Number of new links belonging to the page {len(urls)}")
                urls = list(
                    filter(
                        lambda x: urllib.parse.urlparse(x).path not in self.black_list,
                        urls,
                    )
                )
                logger.info(
                    f"Number of new links after filtering blacklisted {len(urls)}"
                )

            logger.info(f"Found {len(urls)} new urls")

        self.page_structure[url]["time"] = time.time() - start

    def process_all(self):
        for url in self.urls:
            self.process(url)

        self.report_all()
        self.store_all_results()

    def store_result(self, url):
        folder = self.page_structure[url]["url_parse"].netloc.replace(".", "_")

        if not os.path.exists(f"./results/{folder}"):
            os.makedirs(f"./results/{folder}")

        with open(f"./results/{folder}/results.json", "w") as f:
            json.dump(self.page_structure[url]["results"], f, indent=4)

    def store_all_results(self):
        for url in self.urls:
            self.store_result(url)

    def report(self, url):
        total_pages_visited = len(self.page_structure[url]["visited"])
        statistics = ""

        for status_code, quantity in self.page_structure[url]["statistics"].items():
            percentage = quantity / total_pages_visited
            statistics += f"\t {status_code} - {percentage:.2f}\n"

        logger.info(
            f"""
----------------------------------------------------------------------------------
Url: {url}

Total pages visited: {total_pages_visited}

Final statistics: \n{statistics}

It took a total of {self.page_structure[url]['time']:.2f}s to process all pages
----------------------------------------------------------------------------------
        """
        )

    def report_all(self):
        total_time = 0
        total_urls = 0
        for url in self.urls:
            total_time += self.page_structure[url]["time"]
            total_urls += len(self.page_structure[url]["visited"])

        logger.info(
            f"The script ran for a total of {total_time:.2f}s and visited {total_urls} pages"
        )

        for url in self.urls:
            self.report(url)


if __name__ == "__main__":
    urls = ["https://www.snowflake.com/", "https://airflow.apache.org/"]
    urls = ["https://www.ahgora.com/", "https://www.intexfy.com/"]

    WS = WebScrapper(urls=urls, max_depth=3, save_html=True)
    WS.process_all()
