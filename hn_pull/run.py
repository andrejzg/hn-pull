from optparse import OptionParser
from scrapy.crawler import CrawlerProcess
from hn_pull.scraper import Scraper
from scrapy.utils.project import get_project_settings
from scrapy.crawler import Crawler
from scrapy import signals

import logging

logging.getLogger('scrapy').propagate = False

results = []


class MyPipeline(object):
    def __init__(self):
        self.result

    def process_item(self, item, spider):
        self.results.append(item)


def spider_closed(spider):
    print(results)


def main():
    parser = OptionParser()
    parser.add_option("-p", "--posts",
                      help="enter number of posts to be retrieved", dest='posts', default=1)
    (options, args) = parser.parse_args()

    posts = options.posts

    # set up spider
    spider = Scraper()

    # set up settings
    settings = get_project_settings()
    settings.set('ITEM_PIPELINES', {'__main__.MyPipeline':1})

    # set up crawler
    crawler = Crawler(Scraper, settings)
    crawler.signals.connect(spider_closed, signal=signals.spider_closed)

    # start crawling
    crawler.crawl()

if __name__ == "__main__":
    main()
