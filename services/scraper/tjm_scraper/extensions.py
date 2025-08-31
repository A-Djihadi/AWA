"""
Extensions personnalisées pour Scrapy
"""
import logging
from scrapy import signals
from scrapy.exceptions import NotConfigured


class StatsExtension:
    """Extension pour collecter des statistiques de scraping"""
    
    def __init__(self, stats):
        self.stats = stats
        self.logger = logging.getLogger(__name__)
    
    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('STATS_ENABLED', True):
            raise NotConfigured('Stats extension disabled')
        
        ext = cls(crawler.stats)
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(ext.item_dropped, signal=signals.item_dropped)
        
        return ext
    
    def spider_opened(self, spider):
        self.logger.info(f"Spider {spider.name} opened")
    
    def spider_closed(self, spider, reason):
        stats = {
            'items_scraped': self.stats.get_value('item_scraped_count', 0),
            'items_dropped': self.stats.get_value('item_dropped_count', 0),
            'requests_count': self.stats.get_value('downloader/request_count', 0),
            'response_count': self.stats.get_value('downloader/response_count', 0),
            'duration': self.stats.get_value('elapsed_time_seconds', 0),
        }
        
        self.logger.info(f"Spider {spider.name} closed. Stats: {stats}")
    
    def item_scraped(self, item, response, spider):
        pass
    
    def item_dropped(self, item, response, exception, spider):
        self.logger.warning(f"Item dropped: {exception}")
