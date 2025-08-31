#!/usr/bin/env python3
"""
ETL Pipeline Health Check Script
"""
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import orchestrator
    import config
    from loaders import SupabaseLoader
    from extractors import create_extractors, DirectoryExtractor
    
    ETLOrchestrator = orchestrator.ETLOrchestrator
    CONFIG = config.CONFIG
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the ETL directory")
    sys.exit(1)


def check_configuration():
    """Check ETL configuration"""
    print("Configuration Check:")
    print(f"  Supabase URL: {'✓ Set' if CONFIG.supabase_url else '✗ Missing'}")
    print(f"  Supabase Key: {'✓ Set' if CONFIG.supabase_key else '✗ Missing'}")
    print(f"  Source Directory: {CONFIG.data_source_dir}")
    print(f"  Processed Directory: {CONFIG.processed_dir}")
    print(f"  Batch Size: {CONFIG.batch_size}")
    print(f"  Min Quality Score: {CONFIG.min_quality_score}")
    print()


def check_directories():
    """Check required directories"""
    print("Directory Check:")
    
    # Source directory
    source_path = Path(CONFIG.data_source_dir)
    source_exists = source_path.exists()
    print(f"  Source Directory: {'✓' if source_exists else '✗'} {CONFIG.data_source_dir}")
    
    if source_exists:
        jsonl_files = list(source_path.glob("*.jsonl"))
        print(f"    JSONL files found: {len(jsonl_files)}")
    
    # Processed directory
    processed_path = Path(CONFIG.processed_dir)
    try:
        processed_path.mkdir(parents=True, exist_ok=True)
        print(f"  Processed Directory: ✓ {CONFIG.processed_dir}")
    except Exception as e:
        print(f"  Processed Directory: ✗ {CONFIG.processed_dir} ({e})")
    
    # Log directory
    log_path = Path(CONFIG.log_file).parent
    try:
        log_path.mkdir(parents=True, exist_ok=True)
        print(f"  Log Directory: ✓ {log_path}")
    except Exception as e:
        print(f"  Log Directory: ✗ {log_path} ({e})")
    
    print()


def check_database():
    """Check database connection"""
    print("Database Check:")
    
    try:
        loader = SupabaseLoader()
        if loader.health_check():
            print("  Supabase Connection: ✓ OK")
            
            # Get database statistics
            stats = loader.get_statistics()
            if 'error' not in stats:
                print(f"    Total Records: {stats.get('total_records', 'Unknown')}")
                print(f"    Recent Records (24h): {stats.get('recent_records_24h', 'Unknown')}")
            else:
                print(f"    Statistics Error: {stats['error']}")
        else:
            print("  Supabase Connection: ✗ FAILED")
    
    except Exception as e:
        print(f"  Supabase Connection: ✗ ERROR - {e}")
    
    print()


def check_extractors():
    """Check data extractors"""
    print("Extractor Check:")
    
    try:
        extractors = create_extractors()
        directory_extractor = DirectoryExtractor(extractors)
        
        print(f"  Available Extractors: {list(extractors.keys())}")
        
        # Test with empty directory
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            batch, records = directory_extractor.extract_from_directory(temp_dir)
            print(f"  Extractor Test: ✓ OK (empty directory)")
    
    except Exception as e:
        print(f"  Extractor Test: ✗ ERROR - {e}")
    
    print()


def run_pipeline_test():
    """Run a test of the pipeline orchestrator"""
    print("Pipeline Test:")
    
    try:
        orchestrator = ETLOrchestrator()
        
        # Test health checks
        health_ok = orchestrator._run_health_checks()
        print(f"  Health Checks: {'✓ PASS' if health_ok else '✗ FAIL'}")
        
        # Get pipeline stats
        stats = orchestrator.get_pipeline_stats()
        print(f"  Pipeline Stats: ✓ OK")
        print(f"    Total Runs: {stats['runs']}")
        print(f"    Total Processed: {stats['total_processed']}")
        print(f"    Total Loaded: {stats['total_loaded']}")
        
    except Exception as e:
        print(f"  Pipeline Test: ✗ ERROR - {e}")
    
    print()


def main():
    """Main health check routine"""
    
    # Setup basic logging
    logging.basicConfig(level=logging.WARNING)
    
    print("=" * 60)
    print("ETL Pipeline Health Check")
    print("=" * 60)
    print()
    
    # Run all checks
    try:
        check_configuration()
        check_directories()
        check_database()
        check_extractors()
        run_pipeline_test()
        
        print("=" * 60)
        print("Health Check Complete")
        print("=" * 60)
        
    except Exception as e:
        print(f"Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
