import re

import pandas as pd
import scrapy
from navigo.items import NavigoItem
from scrapy import signals


class NavigoSpider(scrapy.Spider):
    name = 'fox_scraper'
    start_urls = ['https://www.fox5ny.com/tag/us/ny/nyc']
    base_url = 'https://www.fox5ny.com/tag/us/ny/nyc?page='
    data = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(NavigoSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response, *args, **kwargs):
        articles = response.xpath('//article')

        for article in articles:
            link = article.xpath('.//h3[@class="title"]/a/@href').get()

            if link and 'video' not in link:
                news_article = NavigoItem(
                    title=article.xpath('.//h3[@class="title"]/a/text()').get(),
                    summary=article.xpath('.//p[@class="dek"]/text()').get(),
                    link=link
                )

                yield scrapy.Request(response.urljoin(link), callback=self.parse_link,
                                     cb_kwargs={'news_article': news_article})

        regex_match = re.match(r'.+?page=(\d+)$', response.url)
        next_page_number = str(int(regex_match.group(1)) + 1) if regex_match else '2'
        next_page_xpath = f'//li[@class="pagi-item pagi-ellip"]/a[text()="{next_page_number}"]'

        if response.xpath(next_page_xpath).get():
            next_page_url = f'{self.base_url}{next_page_number}'
            print(f'LOADING NEXT PAGE: {next_page_url}')

            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_link(self, response, news_article):
        try:
            article_text = ' '.join(response.xpath('//div[@class="article-body"]/p/text()').getall())
        except AttributeError:
            article_text = ''

        news_article['full_article'] = re.sub(r'\s+', ' ', article_text)
        self.data.append(news_article)

    def spider_closed(self, spider, reason):
        df = pd.DataFrame(self.data)
        column_order = ['title', 'summary', 'link', 'full_article']
        df = df[column_order]
        df.to_excel('output.xlsx', index=False)
