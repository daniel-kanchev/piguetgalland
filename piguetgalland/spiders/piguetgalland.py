import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from piguetgalland.items import Article


class PiguetgallandSpider(scrapy.Spider):
    name = 'piguetgalland'
    start_urls = ['https://www.piguetgalland.ch/en/news/']

    def parse(self, response):
        links = response.xpath('//div[@class="card__content"]//h3/a/@href').getall() + \
                response.xpath('//div[@class="card__content"]//div/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)


    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/span/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="tag blank "]/text()').get() or \
               response.xpath('//span[@class="tag blank tag-block"]/text()').get()
        if date:
            date = " ".join(date.strip().split()[2:])

        content = response.xpath('//section[@aria-label="article content"]//div[@class="block-wrap"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
