import csv
import scrapy
import os.path

class ReviewsSpider(scrapy.Spider):
    name = "reviews"
    start_urls = []
    if os.path.exists('output/films.csv'):
        with open("output/films.csv", "r") as f:
            r = csv.DictReader(f)
            start_urls = ['https://letterboxd.com/film/' + item['slug'] + '/reviews/by/added/' for item in r]

    def rating_to_int(self, rating):
        value = 0
        if rating is not None:
            rating = rating.strip()
            for elem in rating:
                if elem == '½':
                    value += 1
                else:
                    value += 2
        return value

    def parse(self, response):
        for review in response.css('.film-detail'):
            item = {
                'user': review.css('.avatar').attrib['href'][1:-1],
                'rating': self.rating_to_int(review.css('.rating::text').get()),
                'film': response.request.url.split("/")[4],
                'liked': 1 if len(review.css('.icon-liked')) > 0 else 0
            }
            yield item

        next_page = response.css('.next').attrib['href']
        if next_page is not None:
            next_page = "https://letterboxd.com" + next_page
            yield response.follow(next_page, self.parse)
