import scrapy
from datetime import datetime, timedelta
from stats.items import OddsItem
from stats.startUrls_results import urls


def calc_ftr(home_score, guest_score):
    if home_score > guest_score:
        result = 'Home'
    elif home_score == guest_score:
        result = 'Draw'
    elif home_score < guest_score:
        result = 'Away'
    else:
        result = ""
    return result


def calc_date(date):
    if date == 'Today':
        dates = datetime.today().strftime('%d.%m.%Y')
    elif date == 'Yesterday':
        dates = datetime.strftime(
            datetime.now() - timedelta(1), '%d.%m.%Y')
    elif len(date) < 8:
        dates = date + '2019'
    else:
        dates = date
    return datetime.strptime(dates, "%d.%m.%Y")


def split_odds(odds):
    if odds:
        odds_1 = float(odds[0])
        odds_x = float(odds[1])
        odds_2 = float(odds[2])
    else:
        odds_1, odds_x, odds_2 = None, None, None
    return (odds_1, odds_x, odds_2)


class QuotesSpider(scrapy.Spider):
    name = "prevGames"
    start_urls = urls
    # start_urls = ['https://www.betexplorer.com/handball/sweden/elitserien-2004-2005/results/?stage=YTUx7d41']

    def parse(self, response):
        country = response.xpath(
            "//a[@class='list-breadcrumb__item__in']//text()")[2].extract()
        season = response.xpath(
            "//h1[@class='wrap-section__header__title']//text()").extract_first()

        for row in response.xpath("//table[contains(@class,'table-main h-mb15')]/tr"):
            if not row.xpath("td[@class='h-text-right h-text-no-wrap']//text()").extract_first():
                print('Round')
                # continue
            else:
                # date TEST
                date = row.xpath(
                    "td[@class='h-text-right h-text-no-wrap']//text()").extract_first()
                date = calc_date(date)

                # score MUST MAKE INTE NOT WORKING NOW
                score = row.xpath(
                    "td[@class='h-text-center']//text()").extract_first()
                home_score = int(score.split(':', 1)[0])
                guest_score = int(score.split(':', 1)[1])
                ftr = calc_ftr(home_score, guest_score)

                # team names
                home_team = row.xpath(
                    "td//a[@class='in-match']/span[position()=1]//text()").extract_first()
                guest_team = row.xpath(
                    "td//a[@class='in-match']/span[position()=2]//text()").extract_first()

                # odds
                odds = row.xpath('td//@data-odd').extract()
                odds_1, odds_x, odds_2 = split_odds(odds)

                # explore ID
                explore_id = 'https://www.betexplorer.com' + row.xpath("td[2]//@href").extract_first()

                oddsItem = OddsItem(
                    country=country,
                    season=season,
                    date=date,
                    score=score,
                    home_score=home_score,
                    guest_score=guest_score,
                    home_team=home_team,
                    guest_team=guest_team,
                    odds_1=odds_1,
                    odds_2=odds_2,
                    odds_x=odds_x,
                    explore_id=explore_id,
                    ftr=ftr
                )
                yield oddsItem
