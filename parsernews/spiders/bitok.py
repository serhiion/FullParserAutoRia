import scrapy
from scrapy.selector import Selector

FORM_DATA = {
    'module': True,
    'unique_content': 'disable',
    'include_category': '2',
    'pagination_number_post': '8',
    'ads_position': '1',
    'current_page': str(2),
    'number_post': '8',
    'excerpt_length': '20',
    'next': True
}


def control():
    counter = int(input("Введіть кількість сторінок: "))
    return counter


class BitkoinList(scrapy.Spider):
    name = 'bitkoin_list'
    start_urls = ['https://bitcoinist.com/']
    pagination_url = 'https://bitcoinist.com/?ajax-request=jnews'
    my_page = 1
    max_page = control()

    def parse(self, response, **kwargs):
        for href in response.xpath("//li[contains(@class,'menu-item "
                                   "menu-item-type-taxonomy "
                                   "menu-item-object-category "
                                   "menu-item-74438 bgnav')]/a/@href"):
            yield response.follow(href, self.pars_next_button)

    def pars_next_button(self, response):
        my_data = {
            "action": "jnews_module_ajax_jnews_block_3",
            "data[current_page]": str(self.my_page),
            "data[attribute][pagination_mode]": "loadmore"
        }
        yield scrapy.FormRequest(
            "https://bitcoinist.com/?ajax-request=jnews",
            method='POST',
            formdata=my_data,
            callback=self.pars_info)

    def pars_info(self, response):
        next_url = (response.json().get("next"))
        info = (response.json().get("content"))
        html_item = Selector(text=info)

        for href in html_item.xpath(
                "//h3[contains(@class,'jeg_post_title')]"
                "/a/@href"):
            yield response.follow(href, self.save_info)

        if next_url and self.my_page <= self.max_page - 1:
            self.my_page += 1
            yield from self.pars_next_button(response)

    def save_info(self, response):
        item = {
            'name_of_group': "Bitcoin",
            'url': response.request.url,
            'title': response.xpath("//h1[contains(@class,'jeg_post_title')]"
                                    "/text()").extract_first('').strip(),
            'authors': response.xpath("//div[contains(@class,'meta_left')]"
                                      "/div[contains(@class,"
                                      " 'jeg_meta_author')]"
                                      "/img/@alt").extract_first('').strip(),
            'date': response.xpath("//div[contains(@class,'meta_left')]"
                                   "/div[contains(@class, 'jeg_meta_date')]"
                                   "/a/text()").extract_first('').strip(),
            'text': response.xpath(
                "//div[contains(@class,'entry-content no-share')]"
                "/div/p/text()").extract()
        }
        yield item
