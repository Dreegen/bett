# To get list of countrys
# § scrapy shell https: // www.betexplorer.com/handball/
response.xpath(
    "//article[@id='upcoming-events-sport-7']//strong//text()").extract()


startUrls = [
    'https://www.betexplorer.com/handball/Austria/',
    'https://www.betexplorer.com/handball/Croatia/',
    'https://www.betexplorer.com/handball/Czech-Republic/',
    'https://www.betexplorer.com/handball/Denmark/',
    'https://www.betexplorer.com/handball/Estonia/',
    'https://www.betexplorer.com/handball/Finland/',
    'https://www.betexplorer.com/handball/France/',
    'https://www.betexplorer.com/handball/Germany/',
    'https://www.betexplorer.com/handball/Greece/',
    'https://www.betexplorer.com/handball/Hungary/',
    'https://www.betexplorer.com/handball/Iceland/',
    'https://www.betexplorer.com/handball/Norway/',
    'https://www.betexplorer.com/handball/Poland/',
    'https://www.betexplorer.com/handball/Portugal/',
    'https://www.betexplorer.com/handball/Romania/',
    'https://www.betexplorer.com/handball/Russia/',
    'https://www.betexplorer.com/handball/Slovakia/',
    'https://www.betexplorer.com/handball/Spain/',
    'https://www.betexplorer.com/handball/Sweden/',
    'https://www.betexplorer.com/handball/Ukraine/'
    ]
