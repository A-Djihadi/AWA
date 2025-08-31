#!/usr/bin/env python3
"""
ETL Data Quality Report Generator
"""
import sys
import json
import logging
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl import ETLOrchestrator, CONFIG
from etl.extractors import DirectoryExtractor, create_extractors
from etl.transformers import StandardTransformer


def analyze_raw_data(source_dir: str, pattern: str = "*.jsonl") -> Dict[str, Any]:
    """Analyze raw extracted data"""
    
    print("Analyzing raw data...")
    
    extractors = create_extractors()
    directory_extractor = DirectoryExtractor(extractors)
    
    batch, raw_records = directory_extractor.extract_from_directory(source_dir, pattern)
    
    if not raw_records:
        return {"error": "No raw data found"}
    
    # Basic statistics
    total_records = len(raw_records)
    sources = Counter(record.get('source', 'unknown') for record in raw_records)
    
    # Field completeness analysis
    field_counts = defaultdict(int)
    for record in raw_records:
        for field in record.keys():
            if record[field] is not None and record[field] != '':
                field_counts[field] += 1
    
    field_completeness = {
        field: count / total_records for field, count in field_counts.items()
    }
    
    return {
        "total_records": total_records,
        "sources": dict(sources),
        "source_files": batch.source_files,
        "field_completeness": dict(sorted(field_completeness.items(), key=lambda x: x[1], reverse=True)),
        "sample_record": raw_records[0] if raw_records else None
    }


def analyze_transformed_data(source_dir: str, pattern: str = "*.jsonl") -> Dict[str, Any]:
    """Analyze transformed data quality"""
    
    print("Analyzing transformed data...")
    
    # Extract raw data
    extractors = create_extractors()
    directory_extractor = DirectoryExtractor(extractors)
    batch, raw_records = directory_extractor.extract_from_directory(source_dir, pattern)
    
    if not raw_records:
        return {"error": "No data to transform"}
    
    # Transform data
    transformer = StandardTransformer()
    offers = []
    transformation_errors = []
    
    for i, record in enumerate(raw_records):
        try:
            offer = transformer.transform(record)
            offers.append(offer)
        except Exception as e:
            transformation_errors.append(f"Record {i}: {str(e)}")
    
    if not offers:
        return {"error": "No valid offers after transformation", "errors": transformation_errors}
    
    # Quality analysis
    quality_scores = [offer.quality_metrics.overall_score for offer in offers if offer.quality_metrics]
    
    # Technology analysis
    all_technologies = []
    for offer in offers:
        all_technologies.extend(offer.technologies)
    tech_counter = Counter(all_technologies)
    
    # Location analysis
    locations = [offer.location.city for offer in offers if offer.location and offer.location.city]
    location_counter = Counter(locations)
    
    # TJM analysis
    tjm_values = []
    for offer in offers:
        if offer.tjm and offer.tjm.is_valid():
            avg_tjm = offer.tjm.get_average()
            if avg_tjm:
                tjm_values.append(avg_tjm)
    
    # Quality issues
    quality_issues = defaultdict(int)
    for offer in offers:
        if offer.quality_metrics and offer.quality_metrics.data_issues:
            for issue in offer.quality_metrics.data_issues:
                quality_issues[issue] += 1
    
    return {
        "total_offers": len(offers),
        "transformation_success_rate": len(offers) / len(raw_records),
        "transformation_errors": transformation_errors[:10],
        "quality_scores": {
            "min": min(quality_scores) if quality_scores else 0,
            "max": max(quality_scores) if quality_scores else 0,
            "avg": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "distribution": {
                "high_quality": sum(1 for s in quality_scores if s >= 0.8),
                "medium_quality": sum(1 for s in quality_scores if 0.6 <= s < 0.8),
                "low_quality": sum(1 for s in quality_scores if s < 0.6),
            }
        },
        "top_technologies": dict(tech_counter.most_common(15)),
        "top_locations": dict(location_counter.most_common(10)),
        "tjm_analysis": {
            "count": len(tjm_values),
            "min": min(tjm_values) if tjm_values else None,
            "max": max(tjm_values) if tjm_values else None,
            "avg": sum(tjm_values) / len(tjm_values) if tjm_values else None,
        },
        "quality_issues": dict(quality_issues.most_common(10)),
        "offers_above_threshold": sum(1 for offer in offers 
                                     if offer.quality_metrics and 
                                     offer.quality_metrics.overall_score >= CONFIG.min_quality_score)
    }


def generate_report(source_dir: str, output_file: str = None):
    """Generate comprehensive data quality report"""
    
    print("=" * 60)
    print("ETL Data Quality Report")
    print("=" * 60)
    print()
    
    # Analyze raw data
    raw_analysis = analyze_raw_data(source_dir)
    
    # Analyze transformed data
    transformed_analysis = analyze_transformed_data(source_dir)
    
    # Create report
    report = {
        "generated_at": str(Path(source_dir)),
        "config": {
            "source_directory": source_dir,
            "min_quality_score": CONFIG.min_quality_score,
            "batch_size": CONFIG.batch_size
        },
        "raw_data_analysis": raw_analysis,
        "transformed_data_analysis": transformed_analysis
    }
    
    # Print summary
    print("RAW DATA ANALYSIS")
    print("-" * 30)
    if "error" in raw_analysis:
        print(f"Error: {raw_analysis['error']}")
    else:
        print(f"Total Records: {raw_analysis['total_records']}")
        print(f"Sources: {', '.join(raw_analysis['sources'].keys())}")
        print(f"Source Files: {len(raw_analysis['source_files'])}")
        print(f"Most Complete Fields:")
        for field, completeness in list(raw_analysis['field_completeness'].items())[:5]:
            print(f"  {field}: {completeness:.1%}")
    
    print()
    print("TRANSFORMED DATA ANALYSIS")
    print("-" * 30)
    if "error" in transformed_analysis:
        print(f"Error: {transformed_analysis['error']}")
    else:
        print(f"Total Offers: {transformed_analysis['total_offers']}")
        print(f"Transformation Success Rate: {transformed_analysis['transformation_success_rate']:.1%}")
        
        quality = transformed_analysis['quality_scores']
        print(f"Quality Scores: Min={quality['min']:.2f}, Max={quality['max']:.2f}, Avg={quality['avg']:.2f}")
        
        dist = quality['distribution']
        print(f"Quality Distribution:")
        print(f"  High (≥0.8): {dist['high_quality']}")
        print(f"  Medium (0.6-0.8): {dist['medium_quality']}")
        print(f"  Low (<0.6): {dist['low_quality']}")
        
        print(f"Offers Above Threshold ({CONFIG.min_quality_score}): {transformed_analysis['offers_above_threshold']}")
        
        tjm = transformed_analysis['tjm_analysis']
        if tjm['count'] > 0:
            print(f"TJM Analysis: {tjm['count']} offers with TJM")
            print(f"  Range: {tjm['min']:.0f}€ - {tjm['max']:.0f}€, Avg: {tjm['avg']:.0f}€")
        
        print(f"Top Technologies:")
        for tech, count in list(transformed_analysis['top_technologies'].items())[:5]:
            print(f"  {tech}: {count}")
    
    # Save report if requested
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\nDetailed report saved to: {output_path}")
    
    print()
    print("=" * 60)


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate ETL Data Quality Report')
    
    parser.add_argument(
        '--source-dir', '-s',
        type=str,
        default=CONFIG.data_source_dir,
        help=f'Source directory (default: {CONFIG.data_source_dir})'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file for detailed JSON report'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        type=str,
        default='*.jsonl',
        help='File pattern to match (default: *.jsonl)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.WARNING)
    
    try:
        generate_report(args.source_dir, args.output)
    
    except Exception as e:
        print(f"Report generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
