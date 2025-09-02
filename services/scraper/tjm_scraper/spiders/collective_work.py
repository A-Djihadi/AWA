"""
AWA TJM Scraper - Collective.work Spider
Production-ready spider for high-volume freelance data extraction
"""

import scrapy
import re
from datetime import datetime
from tjm_scraper.items import TjmOfferItem


class CollectiveWorkSpider(scrapy.Spider):
    name = "collective_work"
    allowed_domains = ["collective.work"]
    start_urls = [
        "https://www.collective.work/job",
        "https://www.collective.work/job?page=2",
        "https://www.collective.work/job?page=3",
    ]
    
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "USER_AGENT": "AWA-TJM-Scraper/2.0",
        "ROBOTSTXT_OBEY": True,
        "AUTOTHROTTLE_ENABLED": True,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scraped_count = 0
        
    def parse(self, response):
        """Parse job listings page"""
        jobs = response.css("div[class*='job']")
        self.logger.info(f"Found {len(jobs)} jobs")
        
        for job in jobs:
            item = self.parse_job_card(job, response)
            if item:
                self.scraped_count += 1
                yield item
    
    def parse_job_card(self, job_element, response):
        """Parse individual job card"""
        try:
            tjm_text = self.extract_tjm(job_element)
            if not tjm_text:
                return None
                
            tjm_min, tjm_max = self.parse_tjm(tjm_text)
            if not tjm_min:
                return None
            
            title = self.extract_text(job_element, ["h2", "h3"]) or "N/A"
            company = self.extract_text(job_element, [".company"]) or "N/A"
            location = self.extract_text(job_element, [".location"]) or "Remote"
            job_url = job_element.css("a::attr(href)").get()
            
            if job_url:
                job_url = response.urljoin(job_url)
                source_id = job_url.split("/")[-1]
            else:
                source_id = f"cw_{hash(title)}"
            
            return TjmOfferItem(
                source="collective_work",
                source_id=source_id,
                url=job_url or response.url,
                title=title,
                company=company,
                location=location,
                tjm_min=tjm_min,
                tjm_max=tjm_max,
                technologies=self.extract_technologies(job_element),
                scraped_at=datetime.now().isoformat(),
                description=self.extract_description(job_element)
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing job: {e}")
            return None
    
    def extract_tjm(self, element):
        """Extract TJM text"""
        all_text = " ".join(element.css("*::text").getall())
        match = re.search(r"(\d+)(?:\s*-\s*(\d+))?\s*[€$]", all_text)
        return f"{match.group(1)}-{match.group(2) or match.group(1)}€" if match else None
    
    def extract_text(self, element, selectors):
        """Extract text using selectors"""
        for selector in selectors:
            text = element.css(f"{selector}::text").get()
            if text and text.strip():
                return text.strip()
        return None
    
    def extract_technologies(self, element):
        """Extract technologies"""
        tech_text = element.css(".expertises *::text, .skills *::text").getall()
        return [t.strip() for t in tech_text if t.strip() and len(t.strip()) > 2][:5]
    
    def extract_description(self, element):
        """Extract description"""
        desc = " ".join(element.css("*::text").getall())
        return desc[:200] if desc else ""
    
    def parse_tjm(self, tjm_text):
        """Parse TJM values"""
        if not tjm_text:
            return None, None
        
        numbers = re.findall(r"\d+", tjm_text)
        if len(numbers) >= 2:
            return int(numbers[0]), int(numbers[1])
        elif len(numbers) == 1:
            value = int(numbers[0])
            return value, value
        
        return None, None
    
    def closed(self, reason):
        """Spider closed"""
        self.logger.info(f"Collective.work closed. Items: {self.scraped_count}")
