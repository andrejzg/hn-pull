import scrapy
import json
from collections import OrderedDict


class Scraper(scrapy.Spider):
    name = "hn-pull"
    allowed_domains = ['news.ycombinator.com']
    start_urls = ['https://news.ycombinator.com/news?p=1',
                  'https://news.ycombinator.com/news?p=2']

    def __init__(self, posts=0):
        super().__init__()
        self.posts = posts
        self.p = 0
        self.results = []

    def parse(self, response):

        for item in response.css('tr.athing'):

            if self.p >= self.posts:
                break

            extracted = [
                ('title', item.css('td.title').xpath('a/text()').extract_first()),
                ('uri', item.css('td.title').xpath('a/@href').extract_first()),
                ('author', item.xpath('following-sibling::tr').css('a.hnuser::text').extract_first()),
                ('points', item.xpath('following-sibling::tr').css('span.score::text').extract_first()),
                ('comments', item.xpath('following-sibling::tr').css('td.subtext').xpath(
                    'a[last()]/text()').extract_first()),
                ('rank', item.css('span.rank::text').extract_first())
            ]

            res = OrderedDict(extracted)

            # parse out points
            res['points'] = int(res['points'].split()[0])

            # parse out rank
            res['rank'] = int(res['rank'][0:-1])

            # parse out comments
            if (res['comments']) == 'discuss':
                res['comments'] = 0
            else:
                res['comments'] = int(res['comments'].split()[0])

            # if internal HN uri append base uri
            if res['uri'].startswith('item?id='):
                res['uri'] = 'https://news.ycombinator.com/{}'.format(res['uri'])

            # run checks
            if not self._passes_checks(res):
                continue

            # add to results
            self.results.append(res)
            self.p += 1

    def dumps(self):
        # pretty print JSON
        print(json.dumps(self.results, indent=4))

    def _passes_checks(self, res):
        # Check title and author are non empty strings not longer than 256 characters
        if (len(res['title']) or len(res['author'])) > 256:
            return False

        # Check points, comments, rank >= 0
        if (res['points'] or res['comments'] or res['rank']) < 0:
            return False

        return True
