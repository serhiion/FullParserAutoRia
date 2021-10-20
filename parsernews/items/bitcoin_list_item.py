from .news_item import NewsItem
import scrapy


class BitcoinListItem(NewsItem):
    name_of_group = scrapy.Field()
