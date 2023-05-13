# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class NavigoItem(Item):
    title = Field()
    full_article = Field()
    summary = Field()
    link = Field()
