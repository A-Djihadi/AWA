#!/usr/bin/env python3
"""
Test ETL Pipeline with Real Data
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set environment variables for Windows paths
os.environ['ETL_SOURCE_DIR'] = str(Path(__file__).parent.parent.parent / 'scraper' / 'data' / 'raw')
os.environ['ETL_PROCESSED_DIR'] = str(Path(__file__).parent.parent / 'data' / 'processed')
os.environ['ETL_LOG_FILE'] = str(Path(__file__).parent.parent / 'logs' / 'etl.log')

try:
    import orchestrator
    
    def test_etl_with_real_data():
        """Test ETL pipeline with actual scraped data"""
        
        print("=" * 60)
        print("ETL Pipeline Test with Real Data")
        print("=" * 60)
        
        # Create orchestrator
        etl = orchestrator.ETLOrchestrator()
        
        # Get source directory
        source_dir = os.environ['ETL_SOURCE_DIR']
        print(f"Source directory: {source_dir}")
        
        # Check if source directory exists and has data
        source_path = Path(source_dir)
        if not source_path.exists():
            print(f"❌ Source directory does not exist: {source_dir}")
            return
        
        # Find JSONL files
        jsonl_files = list(source_path.glob("*.jsonl"))
        if not jsonl_files:
            print(f"❌ No JSONL files found in {source_dir}")
            return
        
        print(f"✅ Found {len(jsonl_files)} JSONL files:")
        for file in jsonl_files:
            print(f"  - {file.name}")
        
        print("\n" + "=" * 60)
        print("Running ETL Pipeline...")
        print("=" * 60)
        
        # Run ETL
        result = etl.run(source_dir)
        
        # Display results
        print("\n" + "=" * 60)
        print("ETL Results")
        print("=" * 60)
        
        if result.get('success'):
            print("✅ ETL Pipeline completed successfully!")
            
            stats = result.get('statistics', {})
            print(f"\nStatistics:")
            print(f"  📥 Extracted Records: {stats.get('extracted_records', 0)}")
            print(f"  🔄 Transformed Offers: {stats.get('transformed_offers', 0)}")
            print(f"  💾 Loaded Offers: {stats.get('loaded_offers', 0)}")
            print(f"  ❌ Failed Offers: {stats.get('failed_offers', 0)}")
            print(f"  📊 Success Rate: {stats.get('success_rate', 0):.1%}")
            print(f"  ⏱️  Duration: {result.get('duration', 0):.2f}s")
            
            if result.get('batch_id'):
                print(f"  🆔 Batch ID: {result['batch_id']}")
        else:
            print("❌ ETL Pipeline failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        # Show phase details
        extraction = result.get('extraction', {})
        if extraction:
            print(f"\n📤 Extraction Phase:")
            print(f"  Files processed: {len(extraction.get('source_files', []))}")
            print(f"  Records extracted: {extraction.get('extracted_count', 0)}")
        
        transformation = result.get('transformation', {})
        if transformation:
            print(f"\n🔄 Transformation Phase:")
            print(f"  Records transformed: {transformation.get('transformed_count', 0)}")
            print(f"  Transformation success rate: {transformation.get('success_rate', 0):.1%}")
        
        loading = result.get('loading', {})
        if loading:
            print(f"\n💾 Loading Phase:")
            print(f"  Records loaded: {loading.get('loaded_count', 0)}")
            print(f"  Loading success: {'✅' if loading.get('success') else '❌'}")
            
            if 'loader_results' in loading:
                print(f"  Loader Results:")
                for loader_name, loader_result in loading['loader_results'].items():
                    status = '✅' if loader_result.get('success') else '❌'
                    print(f"    {loader_name}: {status}")
        
        print("\n" + "=" * 60)
        
        return result
    
    if __name__ == "__main__":
        test_etl_with_real_data()

except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
