import scrapy
from stats.items import QuoteItem
from stats.startUrls import startUrls
# from scrapy.shell import inspect_response


def check_team(response, word):
    if "ht" in word:
        return response.xpath(
            '//*[@id="ctl00_ContentPlaceHolder_homeTeamName"]/text()').extract_first()
    if "gt" in word:
        return response.xpath(
            '//*[@id="ctl00_ContentPlaceHolder_guestTeamName"]/text()').extract_first()


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = startUrls

    def parse(self, response):
        match = response.url[-22:-12]

        gkColumns = [
            "first-column",  # nr
            "second-column",  # namn
            "third-hidden-column hide",  # assist
            "fourth-hidden-column hide",  # teknfel
            "fourth-column",  # mep
            "third-column",  # gk_totRaddning
            "first-hidden-column hide",  # gk_spelRaddning
            "second-hidden-column hide",  # gk_straffRaddning
        ]

        fpColumns = [
            "first-column",  # nr
            "second-column",  # namn
            "third-hidden-column hide",  # assist
            "fourth-hidden-column hide",  # teknfel
            "fourth-column",  # mep
            "first-hidden-column hide",  # fp_totMal
            "first-hidden-column hide",  # fp_spelMal
            "second-hidden-column hide",  # fp_straffmal
            "fifth-hidden-column hide",  # fp_utvisning
        ]

        divNames = [
            "tablecontent flexcontainer ht-gk",
            "tablecontent flexcontainer gt-gk",
            "tablecontent flexcontainer scroll-content ht-fp",
            "tablecontent flexcontainer gt-fp"
        ]

        contentColumns = []
        for j in range(4):
            contentColumns = []

            if "gk" in divNames[j]:
                for i in range(len(gkColumns)):
                    contentColumns.append(response.xpath(
                        '//div[@class="' + divNames[j] + '"]//div[@class=$val]/div//p/text()', val=gkColumns[i]).extract())

                for k in range(len(contentColumns[0])):
                    quoteItem = QuoteItem(
                        match=match,
                        team=check_team(response, divNames[j]),
                        nr=contentColumns[0][k],
                        namn=contentColumns[1][k],
                        assist=contentColumns[2][k],
                        teknFel=contentColumns[3][k],
                        mep=contentColumns[4][k],
                        gk_totRaddning=contentColumns[5][k],
                        gk_spelRaddning=contentColumns[6][k],
                        gk_straffRaddning=contentColumns[7][k],
                        fp_totMal="",
                        fp_spelMal="",
                        fp_straffMal="",
                        fp_utvisning="",
                    )
                    yield quoteItem

            if "fp" in divNames[j]:
                for i in range(len(fpColumns)):
                    contentColumns.append(response.xpath(
                        '//div[@class="' + divNames[j] + '"]//div[@class=$val]/div//p/text()', val=fpColumns[i]).extract())
                for k in range(len(contentColumns[0])):
                    quoteItem = QuoteItem(
                        match=match,
                        team=check_team(response, divNames[j]),
                        nr=contentColumns[0][k],
                        namn=contentColumns[1][k],
                        assist=contentColumns[2][k],
                        teknFel=contentColumns[3][k],
                        mep=contentColumns[4][k],
                        gk_totRaddning="",
                        gk_spelRaddning="",
                        gk_straffRaddning="",
                        fp_totMal=contentColumns[5][k],
                        fp_spelMal=contentColumns[6][k],
                        fp_straffMal=contentColumns[7][k],
                        fp_utvisning=contentColumns[8][k],
                    )
                    yield quoteItem

                    # quoteItem = QuoteItem(match=match, team=team, nr=nr, namn=namn, assist=assist, teknFel=teknFel, mep=mep, gk_totRaddnin=gk_totRaddnin, gk_spelRaddnin=gk_spelRaddnin, gk_straffRaddnin=gk_straffRaddnin, fp_totMal=fp_totMal, fp_spelMal=fp_spelMal, fp_straffMal=fp_straffMal, fp_utvisning=fp_utvisning)
