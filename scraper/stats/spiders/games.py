import scrapy
from stats.items import ResultItem


class QuotesSpider(scrapy.Spider):
    name = "results"
    start_urls = [

    ]

    def parse(self, response):
        date = response.xpath(
            "//div[@class='flexcontainer tablecontent gamedata flexwrap']//div[@class='first-column']//text()").extract()
        lag = response.xpath(
            "//div[@class='flexcontainer tablecontent gamedata flexwrap']//div[@class='second-column']//text()").extract()
        score = response.xpath(
            "//div[@class='flexcontainer tablecontent gamedata flexwrap']//div[@class='third-column']//text()").extract()
        match_url = response.xpath(
            "//div[@class='flexcontainer tablecontent gamedata flexwrap']//a[contains(@href, 'playeranalysis')]/@href").extract()

        for i in range(len(date)):
            resultItem = ResultItem(
                match=match_url[i][-22:-12],
                date=date[i],
                score=score[i],
                home_score=score[i].split('-', 1)[0],
                guest_score=score[i].rsplit('-', 1)[1],
                home_team=lag[i].split('-', 1)[0],
                guest_team=lag[i].rsplit('-', 1)[1],
                match_url="http://213.180.74.118/stat_sve/gamedata/" + match_url[i]
            )
            yield resultItem
