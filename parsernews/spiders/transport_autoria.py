import scrapy


class FullParserAutoRia(scrapy.Spider):
    name = 'parser_auto_ria'
    start_urls = ['https://auto.ria.com/uk/']
    domain = 'https://auto.ria.com'
    page_count = 3

    def parse(self, response, **kwargs):
        for href in response.xpath('//a[@class="elem-tab"]/@href').extract():
            yield response.follow(href, callback=self.pagination)

    def pagination(self, response):
        if response.xpath('//div[contains(@class, "content-bar")]'
                          '/a/@href'):
            for page in range(1, 1 + self.page_count):
                url = f'https://auto.ria.com/uk/car/used/?page={page}'
                yield scrapy.Request(url, callback=self.pars_content_bar)

        if response.xpath('//a[contains(@class, "item-brands last")]/@href'):
            url_category = response.xpath('//a[contains(@class,'
                                          ' "item-brands last")]'
                                          '/@href').extract()
            yield response.follow(self.domain + url_category[0],
                                  callback=self.pars_category_new_auto)

    def pars_content_bar(self, response):
        for href in response.xpath(
                '//div[contains(@class, "content-bar")]'
                '/a/@href'):
            yield response.follow(href, callback=self.save_info_old_positions)

    @staticmethod
    def save_info_old_positions(response):
        item = {
            'status': "Б/У транспорт",
            'url': response.request.url,
            'brand': response.xpath('//h1[contains(@class, "head")]'
                                    '/span/text()').extract_first('').strip(),
            'price': response.xpath('//div[contains(@class, "price_value")]'
                                    '/strong/text()').extract_first('').strip()
        }
        yield item

    def pars_category_new_auto(self, response):
        for href in response.xpath('//a[contains(@class, "item-brands")]'
                                   '/@href'):
            yield response.follow(href, callback=self.pars_new_positions)

    def pars_new_positions(self, response):
        for href in response.xpath('//a[contains(@class,'
                                   ' "gallery-ticket-item d-block")]/@href'):
            yield response.follow(href, callback=self.save_info_new_positions)

    @staticmethod
    def save_info_new_positions(response):
        item = {
            'status': "Новий транспорт",
            'url': response.request.url,
            'brand': response.xpath(
                '//span[contains(@class, "item-link dhide")]'
                '/text()').extract_first('').strip(),
            'price': "Початкова ціна: " + response.xpath(
                '//div[contains(@class, "grey size13")]'
                '/text()').extract_first('').strip()
        }
        yield item

