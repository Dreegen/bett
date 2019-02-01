# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QuoteItem(scrapy.Item):
    match = scrapy.Field()
    team = scrapy.Field()
    nr = scrapy.Field()
    namn = scrapy.Field()
    assist = scrapy.Field()
    teknFel = scrapy.Field()
    mep = scrapy.Field()
    gk_totRaddning = scrapy.Field()
    gk_spelRaddning = scrapy.Field()
    gk_straffRaddning = scrapy.Field()
    fp_totMal = scrapy.Field()
    fp_spelMal = scrapy.Field()
    fp_straffMal = scrapy.Field()
    fp_utvisning = scrapy.Field()


class ResultItem(scrapy.Item):
    date = scrapy.Field()
    match = scrapy.Field()
    score = scrapy.Field()
    home_score = scrapy.Field()
    guest_score = scrapy.Field()
    home_team = scrapy.Field()
    guest_team = scrapy.Field()
    match_url = scrapy.Field()


class OddsItem(scrapy.Item):
    season = scrapy.Field()
    date = scrapy.Field()
    score = scrapy.Field()
    home_score = scrapy.Field()
    guest_score = scrapy.Field()
    home_team = scrapy.Field()
    guest_team = scrapy.Field()
    odds_1 = scrapy.Field()
    odds_2 = scrapy.Field()
    odds_x = scrapy.Field()
    explore_id = scrapy.Field()
    ftr = scrapy.Field()
