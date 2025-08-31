"""
Purge script pour nettoyer les anciennes données
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_supabase_client():
    """Get Supabase client"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        raise ValueError("Missing Supabase credentials")
    
    return create_client(url, key)


def purge_old_offers(client, days_to_keep=90):
    """Purge offers older than specified days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    logger.info(f"Purging offers older than {cutoff_date}")
    
    try:
        # First, get count of records to be deleted
        count_result = client.table('offers').select('count', count='exact').lt('scraped_at', cutoff_date.isoformat()).execute()
        count_to_delete = count_result.count if count_result.count else 0
        
        if count_to_delete == 0:
            logger.info("No old offers to purge")
            return 0
        
        # Delete old offers
        result = client.table('offers').delete().lt('scraped_at', cutoff_date.isoformat()).execute()
        
        deleted_count = len(result.data) if result.data else 0
        logger.info(f"Purged {deleted_count} old offers")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error purging old offers: {e}")
        return 0


def purge_old_raw_offers(client, days_to_keep=30):
    """Purge raw offers older than specified days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    logger.info(f"Purging raw offers older than {cutoff_date}")
    
    try:
        # Get count
        count_result = client.table('raw_offers').select('count', count='exact').lt('scraped_at', cutoff_date.isoformat()).execute()
        count_to_delete = count_result.count if count_result.count else 0
        
        if count_to_delete == 0:
            logger.info("No old raw offers to purge")
            return 0
        
        # Delete old raw offers
        result = client.table('raw_offers').delete().lt('scraped_at', cutoff_date.isoformat()).execute()
        
        deleted_count = len(result.data) if result.data else 0
        logger.info(f"Purged {deleted_count} old raw offers")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error purging old raw offers: {e}")
        return 0


def vacuum_database(client):
    """Run database maintenance"""
    logger.info("Running database vacuum (if supported)")
    
    try:
        # Note: Supabase managed Postgres may not allow manual VACUUM
        # This is more for reference if using self-hosted Postgres
        result = client.rpc('pg_stat_user_tables').execute()
        logger.info("Database statistics retrieved")
        
    except Exception as e:
        logger.warning(f"Could not run vacuum: {e}")


def generate_purge_report(client):
    """Generate purge statistics report"""
    logger.info("Generating purge report")
    
    try:
        # Get table sizes
        offers_count = client.table('offers').select('count', count='exact').execute().count
        raw_offers_count = client.table('raw_offers').select('count', count='exact').execute().count
        snapshots_count = client.table('snapshots').select('count', count='exact').execute().count
        
        # Get oldest/newest records
        oldest_offer = client.table('offers').select('scraped_at').order('scraped_at', desc=False).limit(1).execute()
        newest_offer = client.table('offers').select('scraped_at').order('scraped_at', desc=True).limit(1).execute()
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'table_counts': {
                'offers': offers_count,
                'raw_offers': raw_offers_count,
                'snapshots': snapshots_count
            },
            'date_range': {
                'oldest': oldest_offer.data[0]['scraped_at'] if oldest_offer.data else None,
                'newest': newest_offer.data[0]['scraped_at'] if newest_offer.data else None
            }
        }
        
        logger.info(f"Purge report: {report}")
        return report
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return None


def main():
    """Main purge function"""
    logger.info("Starting data purge process")
    
    try:
        client = get_supabase_client()
        
        # Generate pre-purge report
        logger.info("=== PRE-PURGE REPORT ===")
        pre_report = generate_purge_report(client)
        
        # Purge old data
        logger.info("=== STARTING PURGE ===")
        purged_offers = purge_old_offers(client, days_to_keep=90)
        purged_raw = purge_old_raw_offers(client, days_to_keep=30)
        
        # Database maintenance
        vacuum_database(client)
        
        # Generate post-purge report
        logger.info("=== POST-PURGE REPORT ===")
        post_report = generate_purge_report(client)
        
        logger.info(f"Purge completed successfully:")
        logger.info(f"  - Offers purged: {purged_offers}")
        logger.info(f"  - Raw offers purged: {purged_raw}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Purge process failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
