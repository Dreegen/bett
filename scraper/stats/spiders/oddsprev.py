import os
import pandas as pd
import scrapy
from stats.items import OddsItem

# # imports file to use to Pandas DF
# csvFileName = 'resultLinks.csv'
# csvLoc = os.getcwd()
# # csvSep = ';'
# df = pd.read_csv(csvLoc + csvFileName, sep=csvSep)

class QuotesSpider(scrapy.Spider):
    name = "oddsprev"
    start_urls = ['https://www.betexplorer.com/handball/sweden/handbollsligan/results/',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan/results/',
                  'https://www.betexplorer.com/handball/sweden/she-women/results/',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-women/results/',
                  'https://www.betexplorer.com/handball/sweden/handbollsligan-2017-2018/results/?stage=4h3md1ST',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-2017-2018/results/?stage=Ofozpo3B',
                  'https://www.betexplorer.com/handball/sweden/she-women-2017-2018/results/?stage=0ppJD2c4',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-women-2017-2018/results/?stage=8zDXpZTc',
                  'https://www.betexplorer.com/handball/sweden/handbollsligan-2016-2017/results/?stage=YBwji1fj',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-2016-2017/results/?stage=WSrkEO13',
                  'https://www.betexplorer.com/handball/sweden/she-women-2016-2017/results/?stage=rLgzCt1S',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-women-2016-2017/results/?stage=8AeMvT70',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2015-2016/results/?stage=bwsO16No',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-2015-2016/results/?stage=EHkylDsc',
                  'https://www.betexplorer.com/handball/sweden/elitserien-women-2015-2016/results/?stage=6DT0aOMA',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-women-2015-2016/results/?stage=r1NVUrdr',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2014-2015/results/?stage=n5pinaXp',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-2014-2015/results/?stage=v5tX1xHj',
                  'https://www.betexplorer.com/handball/sweden/elitserien-women-2014-2015/results/?stage=ULBW7KOG',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-women-2014-2015/results/?stage=Cp1y7vvN',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2013-2014/results/?stage=AZT4Oxi5',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-2013-2014/results/?stage=Kvp1tl7N',
                  'https://www.betexplorer.com/handball/sweden/elitserien-women-2013-2014/results/?stage=4rxqvXbm',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-women-2013-2014/results/?stage=UPmc4XeI',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2012-2013/results/?stage=xrqFY8uP',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-2012-2013/results/?stage=Ai3RECV2',
                  'https://www.betexplorer.com/handball/sweden/elitserien-women-2012-2013/results/?stage=lhyJCc4J',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-women-2012-2013/results/?stage=d4cSikOk',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2011-2012/results/?stage=n51hcbDO',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-2011-2012/results/?stage=vubpaKrC',
                  'https://www.betexplorer.com/handball/sweden/elitserien-women-2011-2012/results/?stage=UJqHTara',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-women-2011-2012/results/?stage=84e8VLDn',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2010-2011/results/?stage=vHgVxHVJ',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-2010-2011/results/?stage=hKihwQq5',
                  'https://www.betexplorer.com/handball/sweden/elitserien-women-2010-2011/results/?stage=Ae2mv6Ub',
                  'https://www.betexplorer.com/handball/sweden/allsvenskan-women-2010-2011/results/',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2009-2010/results/?stage=QRxJwWRn',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2008-2009/results/?stage=CUwhFbWG',
                  'https://www.betexplorer.com/handball/sweden/elitserien-women-2008-2009/results/?stage=t2Kb2Z63',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2007-2008/results/?stage=dYlPc27G',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2006-2007/results/?stage=YPd7AOx4',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2005-2006/results/?stage=2PpXUad8',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2004-2005/results/?stage=YTUx7d41',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2003-2004/results/?stage=CEtU8IZl',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2002-2003/results/?stage=bJWTCvCR',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2001-2002/results/?stage=2iwLE0sF',
                  'https://www.betexplorer.com/handball/sweden/elitserien-2000-2001/results/?stage=UwuDGMC2']

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
