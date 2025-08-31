"""
Spider de test simple pour valider la configuration
"""
import scrapy
from tjm_scraper.items import TjmOfferItem


class TestSpider(scrapy.Spider):
    name = 'test'
    allowed_domains = ['httpbin.org']
    start_urls = ['http://httpbin.org/html']

    def parse(self, response):
        """Parse de test simple"""
        self.logger.info(f"Test spider: Got response from {response.url}")
        
        # Créer un item de test
        item = TjmOfferItem(
            source='test',
            source_id='test_001',
            title='Test Job Offer',
            company='Test Company',
            tjm_min=400,
            tjm_max=600,
            tjm_currency='EUR',
            technologies=['Python', 'Scrapy'],
            seniority_level='mid',
            location='Paris',
            remote_policy='hybrid',
            contract_type='freelance',
            description='This is a test job offer for scraper validation',
            url=response.url
        )
        
        yield item
        
        self.logger.info("Test spider: Item yielded successfully")
