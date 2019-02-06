import scrapy
from datetime import datetime, timedelta
from stats.items import OddsItem
from stats.startUrls_results import Austria, Croatia, Czech_republic, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Norway, Poland, Portugal, Romania, Russia, Slovakia, Spain, Sweden, Ukraine


def calc_ftr(score):
    result = []
    h_score = []
    g_score = []
    for i in range(len(score)):
        h_score = score[i].split(':', 1)[0]
        g_score = score[i].split(':', 1)[1]
        if h_score > g_score:
            result.append('1')
        if h_score == g_score:
            result.append('X')
        if h_score < g_score:
            result.append('2')
    return result


def calc_date(date):
    dates = []
    for day in date:
            if day == 'Today':
                dates.append(datetime.today().strftime('%d.%m.%Y'))
            elif day == 'Yesterday':
                dates.append(datetime.strftime(
                    datetime.now() - timedelta(1), '%d.%m.%Y'))
            elif len(day) < 8:
                dates.append(day + '2019')
            else:
                dates.append(day)
    return dates


class QuotesSpider(scrapy.Spider):
    name = "prevGames"
    start_urls = Sweden

    def parse(self, response):
        country = response.xpath(
            "//a[@class='list-breadcrumb__item__in']//text()")[2].extract()
        season = response.xpath(
            "//h1[@class='wrap-section__header__title']//text()").extract_first()
        mainTable = response.xpath("// table[contains(@class, 'table-main h-mb15')]")
        date = mainTable.xpath("//td[@class='h-text-right h-text-no-wrap']//text()").extract()
        date = calc_date(date)
        score = mainTable.xpath("//td[@class='h-text-center']//text()").extract()
        ftr = calc_ftr(score)
        home_team = mainTable.xpath("//a[@class='in-match']//span[position()=1]//text()").extract()
        guest_team = mainTable.xpath(
            "//a[@class='in-match']//span[position()=2]//text()").extract()

        odds_1 = mainTable.xpath(
            "//td[3]//@data-odd").extract()

        odds_x = mainTable.xpath("//td[4]//@data-odd").extract()

        odds_2 = mainTable.xpath("//td[5]//@data-odd").extract()

        explore_id = mainTable.xpath("//td[2]//@href").extract()

        for i in range(len(date)):
            if len(odds_1[i]) < 2 or len(odds_x[i]) < 2 or len(odds_2[i]) < 2:
                odds_1[i] = ""
                odds_2[i] = ""
                odds_x[i] = ""

            oddsItem = OddsItem(
                country=country,
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
