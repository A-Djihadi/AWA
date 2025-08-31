"""
Pipelines pour traiter les items scrappés
"""
import json
import logging
from datetime import datetime
from itemadapter import ItemAdapter
from supabase import create_client, Client


class ValidationPipeline:
    """Pipeline de validation des données"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Validation des champs obligatoires
        required_fields = ['source', 'source_id', 'title']
        for field in required_fields:
            if not adapter.get(field):
                raise ValueError(f"Missing required field: {field}")
        
        # Validation du TJM
        tjm_min = adapter.get('tjm_min')
        tjm_max = adapter.get('tjm_max')
        
        if tjm_min is not None and tjm_min <= 0:
            raise ValueError(f"Invalid tjm_min: {tjm_min}")
        
        if tjm_max is not None and tjm_max <= 0:
            raise ValueError(f"Invalid tjm_max: {tjm_max}")
        
        if tjm_min and tjm_max and tjm_min > tjm_max:
            raise ValueError(f"tjm_min ({tjm_min}) > tjm_max ({tjm_max})")
        
        # Normalisation des technologies
        technologies = adapter.get('technologies', [])
        if technologies:
            # Remove duplicates and normalize
            normalized_techs = list(set([tech.strip().title() for tech in technologies if tech.strip()]))
            adapter['technologies'] = normalized_techs
        
        # Timestamp du scraping
        adapter['scraped_at'] = datetime.utcnow().isoformat()
        
        return item


class DuplicatesPipeline:
    """Pipeline pour éviter les doublons"""
    
    def __init__(self):
        self.seen_items = set()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Créer un identifiant unique
        unique_id = f"{adapter['source']}:{adapter['source_id']}"
        
        if unique_id in self.seen_items:
            logging.warning(f"Duplicate item found: {unique_id}")
            return None
        
        self.seen_items.add(unique_id)
        return item


class SupabasePipeline:
    """Pipeline pour sauvegarder dans Supabase"""
    
    def __init__(self, supabase_url, supabase_key):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client = None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            supabase_url=crawler.settings.get('SUPABASE_URL'),
            supabase_key=crawler.settings.get('SUPABASE_SERVICE_ROLE_KEY'),
        )
    
    def open_spider(self, spider):
        """Initialize Supabase client"""
        if not self.supabase_url or not self.supabase_key:
            spider.logger.warning("Supabase credentials not found, skipping database save")
            return
        
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            spider.logger.info("Supabase client initialized")
        except Exception as e:
            spider.logger.error(f"Failed to initialize Supabase client: {e}")
    
    def process_item(self, item, spider):
        if not self.client:
            return item
        
        adapter = ItemAdapter(item)
        
        try:
            # Prepare data for database
            data = {
                'source': adapter['source'],
                'source_id': adapter['source_id'],
                'title': adapter['title'],
                'company': adapter.get('company'),
                'tjm_min': adapter.get('tjm_min'),
                'tjm_max': adapter.get('tjm_max'),
                'tjm_currency': adapter.get('tjm_currency', 'EUR'),
                'technologies': adapter.get('technologies', []),
                'seniority_level': adapter.get('seniority_level'),
                'location': adapter.get('location'),
                'remote_policy': adapter.get('remote_policy'),
                'contract_type': adapter.get('contract_type', 'freelance'),
                'description': adapter.get('description'),
                'url': adapter.get('url'),
                'scraped_at': adapter.get('scraped_at'),
            }
            
            # Insert or update
            result = self.client.table('offers').upsert(
                data,
                on_conflict='source,source_id'
            ).execute()
            
            if result.data:
                spider.logger.info(f"Saved offer to database: {adapter['source']}:{adapter['source_id']}")
            else:
                spider.logger.warning(f"No data returned from upsert: {adapter['source']}:{adapter['source_id']}")
            
        except Exception as e:
            spider.logger.error(f"Failed to save to Supabase: {e}")
        
        return item


class JsonFilesPipeline:
    """Pipeline pour sauvegarder en fichiers JSON"""
    
    def __init__(self):
        self.files = {}
    
    def open_spider(self, spider):
        """Open JSON file for writing"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"/app/data/raw/{spider.name}_{timestamp}.jsonl"
        
        try:
            self.files[spider] = open(filename, 'w', encoding='utf-8')
            spider.logger.info(f"Opened JSON file: {filename}")
        except Exception as e:
            spider.logger.error(f"Failed to open JSON file: {e}")
    
    def close_spider(self, spider):
        """Close JSON file"""
        if spider in self.files:
            self.files[spider].close()
            del self.files[spider]
    
    def process_item(self, item, spider):
        if spider in self.files:
            try:
                line = json.dumps(dict(item), ensure_ascii=False) + '\n'
                self.files[spider].write(line)
                self.files[spider].flush()
            except Exception as e:
                spider.logger.error(f"Failed to write to JSON file: {e}")
        
        return item
