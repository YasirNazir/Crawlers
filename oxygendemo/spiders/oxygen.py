# -*- coding: utf-8 -*-
__author__ = 'Yasir'
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from oxygendemo.items import OxygendemoItem
import re
import pyquery
import urlparse


class OxygenSpider(CrawlSpider):
    name = "oxygenboutique.com"
    allowed_domains = ["oxygenboutique.com"]
    start_urls = ['http://www.oxygenboutique.com']

    xpaths = {
        'pp_type': '',

        'pp_gender': '',

        'pp_designer': '//div[@class="brand_name"]/a/text()',

        'pp_name': '//div[@id="container"]//h2/text()',

        'pp_description': '(//div[@id="accordion"][h3[contains(text(),"Description")]]'
                          '//following-sibling::div)[1]//text()',

        'pp_raw_color': '',

        'pp_image_urls': '//div[@id="thumbnails-container"]//a[@class="cloud-zoom-gallery"]/@href',

        'pp_gbp_price': '//span[@class="price geo_16_darkbrown"]/text() | '
                        '//span[@class="price geo_16_darkbrown"]//span[@class="offsetMark"]/text()',

        'pp_sale_discount': '//span[@class="price geo_16_darkbrown"]/span/text()',

        'pp_stock_status': '//select[@id="ctl00_ContentPlaceHolder1_ddlSize"]/option[position()>1]',
    }

    # Types
    TYPES = {
        'apparel': 'A',
        'shoes': 'S',
        'bags': 'B',
        'jewelry': 'J',
        'accessories': 'R'
    }

    # Gender
    GENDER = {
        'male': 'M',
        'female': 'F',
    }
    rules = (
        Rule(SgmlLinkExtractor(
            restrict_xpaths=['//div[@class="itm"]//table'],
            unique=True,
        ),
            callback='parse_item',
            follow=True
        ),

        Rule(SgmlLinkExtractor(
            unique=True,
            restrict_xpaths=[
                '//div[@class="all_items"]',
                '//ul[@class="topnav"]/li/a',
                '//a[@class="NextPage"]'
            ]
        ),
            follow=True
        ),
    )

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        pp = hxs.select("//body[@id='product_page']")
        if pp:
            self.pq = pyquery.PyQuery(response.body)
            item = OxygendemoItem()

            # Type
            # Todo

            # Gender
            # Todo
            # item['gender'] = 'F'

            # Designer
            tmp = hxs.select(self.xpaths['pp_designer']).extract()
            if tmp:
                item['designer'] = tmp[0].strip()

            # Code
            tmp = response.url
            code = re.findall("([A-z\-]+)\.aspx", tmp)
            if code:
                item['code'] = code[0].strip()

            # Description
            tmp = hxs.select(self.xpaths['pp_description']).extract()
            if tmp:
                item['description'] = '\n'.join(map(lambda s: s.strip(), tmp)).strip()

            # Price
            tmp = hxs.select(self.xpaths['pp_gbp_price']).extract()
            if tmp[0] == '':
                tmp = hxs.select("//span[@class='offsetMark']/text()").extract()
                pound = unichr(163)
                gbp_price = re.sub('['+pound+'|\s|,]', '', ''.join(tmp[0]))
                item['gbp_price'] = gbp_price
            else:
                pound = unichr(163)
                gbp_price = re.sub('['+pound+'|\s|,]', '', ''.join(tmp[0]))
                item['gbp_price'] = gbp_price

            # Images
            images = hxs.select(self.xpaths['pp_image_urls']).extract()
            item['image_urls'] = [urlparse.urljoin(response.url, image.strip()) for image in images]

            # Name
            tmp = hxs.select(self.xpaths['pp_name']).extract()
            if tmp:
                item['name'] = tmp[0].strip()

            # Sale-discount
            tmp = hxs.select("//span[@class='price geo_16_darkbrown']/span[2]/text()").extract()
            if tmp:
                item['sale_discount'] = tmp[0].strip()

            # source URL
            item['source_url'] = response.url

            # StockStatus
            tmps = hxs.select(self.xpaths['pp_stock_status'])
            size_dict = {}
            for tmp in tmps:
                option = tmp.select('./text()').extract()[0]
                option_regex = re.findall("(?:([A-Z]{1,2}|\d{1,2})[\s\*-]*(Sold\sOut)?)", option)
                if option_regex[0][1].lower() == "sold out":
                    size_dict[option_regex[0][1]] = 3
                else:
                    size_dict[option_regex[0][1]] = 1
            yield item
