# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class OxygendemoItem(Item):
    # define the fields for your item here like:
    type = Field()
    gender = Field()
    designer = Field()
    code = Field()
    name = Field()
    description = Field()
    raw_color = Field()
    image_urls = Field()
    gbp_price = Field()
    sale_discount = Field()
    stock_status = Field()
    source_url = Field()