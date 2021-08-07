# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonspiderItem(scrapy.Item):
      title = scrapy.Field()
      brand = scrapy.Field()
      price = scrapy.Field()
      desc = scrapy.Field()
      bullets = scrapy.Field()
      stars = scrapy.Field()
     
