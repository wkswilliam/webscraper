WebScraper Class
The WebScraper class in Python is a tool for crawling and processing web pages. It takes specified URLs, processes them up to a defined depth, and stores the results locally. It can exclude specific URLs and optionally save HTML content.

Features
Crawl URLs: Processes a list of given URLs.
Control Depth: Limits the crawling depth for managing load and relevance.
Blacklist URLs: Avoids specific URLs during the crawl.
Save HTML: Stores HTML content of crawled pages if required.
Statistics Output: Provides statistics on the crawl process.
Parameters
Input Parameters
urls: list of str
A list of URLs to start crawling from.

max_depth: int
Defines the maximum depth for crawling links. For example, max_depth=1 will only crawl links on the initial pages, while max_depth=2 will go one level deeper, and so on.

black_list: list of str
A list of URLs or patterns to exclude from the crawl. These URLs will be skipped if encountered during the crawl.

save_html: bool
If True, saves the HTML content of each processed page to a local directory. If False, only the statistics will be stored.

Methods
process_all()
This method performs the crawling operation. It:

Visits each URL in urls.
Follows links up to max_depth while respecting black_list.
Optionally saves the HTML content to a local directory if save_html is set to True.
At the end, outputs statistics about the crawl process, such as the number of URLs processed, the time taken, and the count of skipped URLs.
Output
Results Directory: All results are stored in a local folder named results/ (or any other specified path).
Statistics: Printed at the end, including:
Total URLs processed.
Total time taken.
Additional details as needed.
Usage Example
python
Copy code
from your_module import WebScraper

# Define parameters
urls = ["https://example.com", "https://another-example.com"]
max_depth = 2
black_list = ["https://example.com/ignore"]
save_html = True

# Instantiate and run
scraper = WebScraper(urls=urls, max_depth=max_depth, black_list=black_list, save_html=save_html)
scraper.process_all()
This example will process urls, skip URLs in black_list, save HTML content, and print crawl statistics.

## Or...

After installing the required packages and activating the virtualenv just run in the terminal:

python scraper.py | tail -f output.log

# Requirements
Python 3.8+
Required packages: defined in the requirements.txt file