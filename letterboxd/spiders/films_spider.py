import scrapy
from scrapy import Request
from scrapy.exceptions import CloseSpider


class FilmsSpider(scrapy.Spider):
    name = "films"
    start_urls = [
        'https://letterboxd.com/films/ajax/by/release-earliest/size/small/',
    ]

    def parse_film(self, response):
        film = {
            'title': response.css('.prettify')[0].css("*::text").get(),
            'director': response.css('.prettify')[1].css("*::text").get(),
            'year':  response.css('.number')[0].css("*::text").get(),
            'tmdb': response.css('.track-event')[-1].attrib['href'].split("/")[-2],
            'genres': list(map(lambda res: res.get(), response.css('div[id=tab-genres]').css(".text-slug::text"))),
        }

        if film['director'] is "\n\t\t\t\t\t\t":
            film['director'] = None

        if film['year'] is not None:
            film['year'] = int(film['year'])
        else:
            raise CloseSpider('No year found')

        if film['year'] > 2022:
            raise CloseSpider('Reached end of films')

        if film['tmdb'] is not None:
            film['tmdb'] = int(film['tmdb'])

        yield film

    def parse(self, response):
        for film in response.css('.poster-container'):
            film_link = 'https://letterboxd.com' + \
                film.css('.film-poster').attrib['data-target-link']
            yield Request(film_link, callback=self.parse_film)

        next_page = response.css('.next').attrib['href']
        if next_page is not None:
            next_page = "https://letterboxd.com/films/ajax/by/release-earliest/size/small/page/" + \
                next_page.split("/")[-2]
            yield response.follow(next_page, self.parse)
