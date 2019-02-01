import os
import scrapy
from stats.items import OddsItem


class QuotesSpider(scrapy.Spider):
    name = "oddsprev"
    start_urls = ['file://´'+os.getcwd()+'/explore_html/1.html',
                  'file://´'+os.getcwd()+'/explore_html/2.html',
                  'file://´'+os.getcwd()+'/explore_html/3.html',
                  'file://´'+os.getcwd()+'/explore_html/4.html',
                  'file://´'+os.getcwd()+'/explore_html/5.html',
                  'file://´'+os.getcwd()+'/explore_html/6.html',
                  'file://´'+os.getcwd()+'/explore_html/7.html',
                  'file://´'+os.getcwd()+'/explore_html/8.html',
                  'file://´'+os.getcwd()+'/explore_html/9.html',
                  'file://´'+os.getcwd()+'/explore_html/10.html',
                  'file://´'+os.getcwd()+'/explore_html/11.html',
                  'file://´'+os.getcwd()+'/explore_html/12.html',
                  'file://´'+os.getcwd()+'/explore_html/13.html',
                  'file://´'+os.getcwd()+'/explore_html/14.html', ]

    def parse(self, response):
        season = response.xpath(
            "//h1[@class='wrap-section__header__title']//text()").extract_first()

        # if yesterday or tooday
        date = response.xpath(
            "//*[@id='js-leagueresults-all']//td[@class='h-text-right h-text-no-wrap']//text()").extract()
        for i in range(len(date)):
            if len(date[i]) < 8:
                date[i] = date[i] + "2018"
            if date == 'yesterday':
                date[i] = '18.12.2018'

        score = response.xpath(
            "//*[@id='js-leagueresults-all']//td[@class='h-text-center']//text()").extract()

        ftr = []
        for i in range(len(score)):
            home_score = score[i].split(':', 1)[0]
            guest_score = score[i].split(':', 1)[1]
            if home_score > guest_score:
                ftr.append('1')
            if home_score == guest_score:
                ftr.append('X')
            if home_score < guest_score:
                ftr.append('2')

        home_team = response.xpath(
            "//div[@id='js-leagueresults-all']//a[@class='in-match']//span[position()=1]//text()").extract()

        guest_team = response.xpath(
            "//div[@id='js-leagueresults-all']//a[@class='in-match']//span[position()=2]//text()").extract()

        odds_1 = response.xpath("//*[@id='js-leagueresults-all']//td[3]//text()").extract()

        odds_x = response.xpath("//*[@id='js-leagueresults-all']//td[4]//text()").extract()

        odds_2 = response.xpath("//*[@id='js-leagueresults-all']//td[5]//text()").extract()

        for i in range(len(odds_1)):
            if odds_1[i] == "\xa0":
                odds_1[i] = ""
            if odds_x[i] == "\xa0":
                odds_x[i] = ""
            if odds_2[i] == "\xa0":
                odds_2[i] = ""

        explore_id = response.xpath("//*[@id='js-leagueresults-all']//td[2]//@href").extract()

        for i in range(len(date)):
            oddsItem = OddsItem(
                season=season,
                date=date[i],
                score=score[i],
                home_score=score[i].split(':', 1)[0],
                guest_score=score[i].split(':', 1)[1],
                home_team=home_team[i],
                guest_team=guest_team[i],
                odds_1=odds_1[i],
                odds_2=odds_2[i],
                odds_x=odds_x[i],
                explore_id=explore_id[i].rsplit('/', 2)[1],
                ftr=ftr[i]
            )
            yield oddsItem
