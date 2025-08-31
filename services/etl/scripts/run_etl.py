#!/usr/bin/env python3
"""
ETL Pipeline Runner Script
Usage: python run_etl.py [options]
"""
import argparse
import logging
import sys
import json
from pathlib import Path

# Add parent directory to path to import etl module
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl import run_etl, CONFIG


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(CONFIG.log_file, encoding='utf-8')
        ]
    )


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description='Run ETL Pipeline')
    
    parser.add_argument(
        '--source-dir', '-s',
        type=str,
        default=CONFIG.data_source_dir,
        help=f'Source directory for data files (default: {CONFIG.data_source_dir})'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        type=str,
        default='*.jsonl',
        help='File pattern to match (default: *.jsonl)'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        type=str,
        default=CONFIG.log_level,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help=f'Logging level (default: {CONFIG.log_level})'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file for results JSON'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run pipeline without loading data'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger('etl_runner')
    
    if not args.quiet:
        print("=" * 60)
        print("ETL Pipeline Runner")
        print("=" * 60)
        print(f"Source Directory: {args.source_dir}")
        print(f"File Pattern: {args.pattern}")
        print(f"Log Level: {args.log_level}")
        if args.dry_run:
            print("Mode: DRY RUN (no data will be loaded)")
        print("=" * 60)
    
    try:
        # Check source directory
        source_path = Path(args.source_dir)
        if not source_path.exists():
            logger.error(f"Source directory does not exist: {args.source_dir}")
            sys.exit(1)
        
        # Count files to process
        files = list(source_path.glob(args.pattern))
        if not files:
            logger.warning(f"No files found matching pattern '{args.pattern}' in {args.source_dir}")
            sys.exit(0)
        
        if not args.quiet:
            print(f"Found {len(files)} files to process:")
            for file in files[:5]:  # Show first 5 files
                print(f"  - {file.name}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")
            print()
        
        # Run ETL pipeline
        logger.info("Starting ETL pipeline...")
        
        if args.dry_run:
            # TODO: Implement dry run mode
            logger.info("Dry run mode not yet implemented")
            result = {"success": False, "error": "Dry run mode not implemented"}
        else:
            result = run_etl(args.source_dir, args.pattern)
        
        # Output results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            
            logger.info(f"Results written to: {output_path}")
        
        # Print summary
        if not args.quiet:
            print("\n" + "=" * 60)
            print("ETL Pipeline Results")
            print("=" * 60)
            
            if result.get("success"):
                stats = result.get("statistics", {})
                print(f"✓ Pipeline completed successfully")
                print(f"  Duration: {result.get('duration', 0):.2f} seconds")
                print(f"  Extracted: {stats.get('extracted_records', 0)} records")
                print(f"  Transformed: {stats.get('transformed_offers', 0)} offers")
                print(f"  Loaded: {stats.get('loaded_offers', 0)} offers")
                print(f"  Success Rate: {stats.get('success_rate', 0):.2%}")
                
                if result.get("batch_id"):
                    print(f"  Batch ID: {result['batch_id']}")
            
            else:
                print(f"✗ Pipeline failed: {result.get('error', 'Unknown error')}")
                if result.get('duration'):
                    print(f"  Duration: {result['duration']:.2f} seconds")
            
            print("=" * 60)
        
        # Exit with appropriate code
        sys.exit(0 if result.get("success") else 1)
    
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"Pipeline failed with exception: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
