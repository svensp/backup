import argparse
import time
from datetime import datetime
from datetime import timedelta
from prometheus_client import start_http_server
from prometheus_client import Gauge
from .command import Command

class PrometheusMetricsCommand(Command):
    def __init__(self):
        self._name = "prometheus:metrics"
        self._description('Start a prometheus metrics endpoint')

    def setBorg(self, borg):
        self._borg = borg
        return self

    def setMySQL(self, mysql):
        self._mysql = mysql
        return self

    def run(self, parameters):
        self.__parseArgs(parameters)
        self._latestMysql = Gauge('cloudbackup_mysql_latest_timestamp',
                'Latest backup',
                ['resort']
                )
        self._latestBorg = Gauge('cloudbackup_borg_latest_timestamp',
                'Latest backup',
                ['resort', 'repository']
                )

        for resort in self._storage.getResorts():
            resort.passAdapters(self)

        self.__initialScrape()
        start_http_server(self._args.port)

        self.__scrapeLoop()

    def __initialScrape(self):
        self.__scrape()

    def __scrapeLoop(self):
        while True:
            self.__scrape()
            self.__waitInterval()

    def __scrape(self):
        self._storage.load()
        self._lastScrapeStart = datetime.now()

        print('Scraping')

        for resort in self._storage.getResorts():
            print("Scraping "+resort._name)
            resort.passAdapters(self)
            if self._borg:
                self._borg.scrape(self._latestBorg)

            if self._mysql:
                self._mysql.scrape(self._latestMysql)
                
        print('Scraped')

    def __waitInterval(self):
        nextScrape = self.__calculateNextScrape()
        sleepTime = self.__calculateSleepTime(nextScrape)
        print("Sleeping for "+str(sleepTime.seconds))
        time.sleep(sleepTime.seconds)

    def __calculateNextScrape(self):
        return self._lastScrapeStart + timedelta(minutes=self._args.interval)

    def __calculateSleepTime(self, nextScrape):
        return nextScrape - datetime.now()

    def __parseArgs(self, parameters):
        parser = argparse.ArgumentParser()
        parser.add_argument('--interval',
                required=False,
                default=15,
                help='Interval in minutes between scrapes',
                type=int
                )
        parser.add_argument('--port',
                required=False,
                default=8000,
                help='Port on which the metrics http server is exposed.',
                type=int
                )
        self._args = parser.parse_args(parameters)
