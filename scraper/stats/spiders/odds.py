import scrapy
from stats.items import OddsItem
import os


class QuotesSpider(scrapy.Spider):
    name = "odds"
    path = 'file://´' + os.getcwd() + '/explore_html/0.html'
    start_urls = [path, ]

    def parse(self, response):
        season = response.xpath(
            "//h1[@class='wrap-section__header__title']//text()").extract_first()

        # if yesterday or tooday
        date = response.xpath(
            "//*[@id='js-leagueresults-all']//td[@class='h-text-right h-text-no-wrap']//text()").extract()

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

        odds_1 = response.xpath("//*[@id='js-leagueresults-all']//td[3]//@data-odd").extract()

        odds_x = response.xpath("//*[@id='js-leagueresults-all']//td[4]//@data-odd").extract()

        odds_2 = response.xpath("//*[@id='js-leagueresults-all']//td[5]//@data-odd").extract()

        explore_id = response.xpath("//*[@id='js-leagueresults-all']//td[2]//@href").extract()

        for i in range(len(date)):
            oddsItem = OddsItem(
                season=season,
                date=date[i] + "2018",
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
