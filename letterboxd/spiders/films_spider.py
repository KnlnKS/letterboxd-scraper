import scrapy
from scrapy.exceptions import CloseSpider


class FilmsSpider(scrapy.Spider):
    name = "films"
    start_urls = [
        'https://letterboxd.com/films/ajax/by/release-earliest/size/small/',
    ]

    def parse(self, response):
        slugs = []
        for film in response.css('.poster-container'):
            slugs.append(film.css('.poster').attrib['data-film-slug'][6:-1])

        for slug in slugs:
            yield {'slug': slug}

        next_page = response.css('.next').attrib['href']
        if next_page is not None:
            page_num = int(next_page.split("/")[-2])
            if page_num > 9250:
                CloseSpider("End of films")
            next_page = "https://letterboxd.com/films/ajax/by/release-earliest/size/small/page/" + \
                next_page.split("/")[-2]
            yield response.follow(next_page, self.parse)
