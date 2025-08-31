"""
AWA Data Analyzer

Comprehensive analysis tool for scraped TJM data.
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter
import argparse


def load_data(data_file: Path) -> list:
    """Load data from JSON or JSONL file"""
    if data_file.suffix == '.json':
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif data_file.suffix == '.jsonl':
        data = []
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line.strip()))
        return data
    else:
        raise ValueError(f"Unsupported file format: {data_file.suffix}")


def analyze_scraped_data(data_file: Path):
    """
    Comprehensive analysis of scraped data
    
    Args:
        data_file: Path to the data file
    """
    print(f"\n{'='*80}")
    print(f"AWA TJM DATA ANALYSIS")
    print(f"{'='*80}")
    print(f"File: {data_file}")
    print(f"Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        data = load_data(data_file)
    except Exception as e:
        print(f"ERROR: Failed to load data - {e}")
        return
    
    if not data:
        print("ERROR: No data found in file")
        return
    
    print(f"Total offers: {len(data)}")
    
    # Run analyses
    analyze_quality(data)
    analyze_tjm(data)
    analyze_technologies(data)
    analyze_locations(data)
    analyze_companies(data)
    
    print(f"\n{'='*80}")
    print("Analysis completed successfully!")
    print(f"{'='*80}")


def analyze_quality(data: list):
    """Analyze data quality metrics"""
    print(f"\n{'-'*60}")
    print("DATA QUALITY ANALYSIS")
    print(f"{'-'*60}")
    
    total = len(data)
    quality_metrics = {
        'title': sum(1 for item in data if item.get('title')),
        'company': sum(1 for item in data if item.get('company')),
        'tjm_min': sum(1 for item in data if item.get('tjm_min')),
        'tjm_max': sum(1 for item in data if item.get('tjm_max')),
        'technologies': sum(1 for item in data if item.get('technologies')),
        'location': sum(1 for item in data if item.get('location')),
        'description': sum(1 for item in data if item.get('description'))
    }
    
    for field, count in quality_metrics.items():
        percentage = (count / total) * 100
        print(f"{field:15}: {count:4}/{total:4} ({percentage:5.1f}%)")
    
    # Overall quality score
    avg_completeness = sum(quality_metrics.values()) / (len(quality_metrics) * total) * 100
    print(f"{'Overall quality':15}: {avg_completeness:5.1f}%")


def analyze_tjm(data: list):
    """Analyze TJM rates"""
    print(f"\n{'-'*60}")
    print("TJM ANALYSIS")
    print(f"{'-'*60}")
    
    # Extract TJM values
    tjm_values = []
    for item in data:
        tjm_min = item.get('tjm_min')
        tjm_max = item.get('tjm_max')
        
        if tjm_min is not None:
            tjm_values.append(tjm_min)
        if tjm_max is not None and tjm_max != tjm_min:
            tjm_values.append(tjm_max)
    
    if not tjm_values:
        print("No TJM data found")
        return
    
    # Statistical analysis
    tjm_array = np.array(tjm_values)
    print(f"Total TJM values: {len(tjm_values)}")
    print(f"Mean TJM: {np.mean(tjm_array):.2f} EUR")
    print(f"Median TJM: {np.median(tjm_array):.2f} EUR")
    print(f"Min TJM: {np.min(tjm_array):.2f} EUR")
    print(f"Max TJM: {np.max(tjm_array):.2f} EUR")
    print(f"Std Dev: {np.std(tjm_array):.2f} EUR")
    
    # Percentiles
    percentiles = [25, 50, 75, 90, 95]
    print("\nPercentiles:")
    for p in percentiles:
        value = np.percentile(tjm_array, p)
        print(f"P{p:2}: {value:.2f} EUR")


def analyze_technologies(data: list):
    """Analyze technology distribution"""
    print(f"\n{'-'*60}")
    print("TECHNOLOGY ANALYSIS")
    print(f"{'-'*60}")
    
    # Count technologies
    tech_counter = Counter()
    tech_offers_count = 0
    
    for item in data:
        technologies = item.get('technologies', [])
        if technologies:
            tech_offers_count += 1
            for tech in technologies:
                if tech:  # Avoid empty strings
                    tech_counter[tech.strip()] += 1
    
    print(f"Offers with technologies: {tech_offers_count}/{len(data)}")
    print(f"Unique technologies: {len(tech_counter)}")
    
    if tech_counter:
        print(f"\nTop 15 technologies:")
        for tech, count in tech_counter.most_common(15):
            percentage = (count / tech_offers_count) * 100
            print(f"{tech:20}: {count:3} ({percentage:5.1f}%)")


def analyze_locations(data: list):
    """Analyze location distribution"""
    print(f"\n{'-'*60}")
    print("LOCATION ANALYSIS")
    print(f"{'-'*60}")
    
    location_counter = Counter()
    location_offers_count = 0
    
    for item in data:
        location = item.get('location')
        if location:
            location_offers_count += 1
            location_counter[location.strip()] += 1
    
    print(f"Offers with location: {location_offers_count}/{len(data)}")
    print(f"Unique locations: {len(location_counter)}")
    
    if location_counter:
        print(f"\nTop 10 locations:")
        for location, count in location_counter.most_common(10):
            percentage = (count / location_offers_count) * 100
            print(f"{location:30}: {count:3} ({percentage:5.1f}%)")


def analyze_companies(data: list):
    """Analyze company distribution"""
    print(f"\n{'-'*60}")
    print("COMPANY ANALYSIS")
    print(f"{'-'*60}")
    
    company_counter = Counter()
    company_offers_count = 0
    
    for item in data:
        company = item.get('company')
        if company:
            company_offers_count += 1
            company_counter[company.strip()] += 1
    
    print(f"Offers with company: {company_offers_count}/{len(data)}")
    print(f"Unique companies: {len(company_counter)}")
    
    if company_counter:
        print(f"\nTop 10 companies:")
        for company, count in company_counter.most_common(10):
            percentage = (count / company_offers_count) * 100
            print(f"{company:30}: {count:3} ({percentage:5.1f}%)")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Analyze scraped TJM data")
    parser.add_argument("file", help="Data file to analyze (JSON or JSONL)")
    parser.add_argument("--export", help="Export analysis to file")
    
    args = parser.parse_args()
    
    data_file = Path(args.file)
    if not data_file.exists():
        print(f"ERROR: File not found: {data_file}")
        return 1
    
    analyze_scraped_data(data_file)
    return 0


if __name__ == "__main__":
    exit(main())
