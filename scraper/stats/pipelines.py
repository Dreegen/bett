# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import psycopg2
import stats.items as items


class StatsPipeline(object):

    def open_spider(self, spider):
        hostname = 'localhost'
        username = 'hallberg'
        password = ''
        database = 'bett'
        self.connection = psycopg2.connect(
            host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):
        if isinstance(item, items.QuoteItem):
            self.cur.execute("insert into matchData(match, team, nr, namn, assist, teknFel, mep, gk_totRaddning, gk_spelRaddning, gk_straffRaddning, fp_totMal, fp_spelMal, fp_straffMal, fp_utvisning) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
                item['match'], item['team'], item['nr'], item['namn'], item['assist'], item['teknFel'], item['mep'], item['gk_totRaddning'], item['gk_spelRaddning'], item['gk_straffRaddning'], item['fp_totMal'], item['fp_spelMal'], item['fp_straffMal'], item['fp_utvisning']))
            self.connection.commit()
            return item

        if isinstance(item, items.ResultItem):
            self.cur.execute("insert into matchResults(date, match,score, home_score, guest_score, home_team, guest_team, match_url) values(%s,%s,%s,%s,%s,%s,%s,%s)",
                             (item['date'], item['match'], item['score'], item['home_score'], item['guest_score'], item['home_team'], item['guest_team'], item['match_url']))
            self.connection.commit()
            return item

        if isinstance(item, items.OddsItem):
            self.cur.execute("insert into odds(country, season, date, score, home_score, guest_score, home_team, guest_team, odds_1, odds_x, odds_2, explore_id, ftr) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                             (item['country'], item['season'], item['date'], item['score'], item['home_score'], item['guest_score'], item['home_team'], item['guest_team'], item['odds_1'], item['odds_x'], item['odds_2'], item['explore_id'], item['ftr']))
            self.connection.commit()
            return item
