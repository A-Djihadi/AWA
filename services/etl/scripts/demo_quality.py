#!/usr/bin/env python3
"""
ETL Pipeline Quality Analysis Demo
"""
import sys
import os
from pathlib import Path

# Add parent directory to path and configure paths
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ['ETL_SOURCE_DIR'] = str(Path(__file__).parent.parent.parent / 'scraper' / 'data' / 'raw')

try:
    from extractors import DirectoryExtractor, create_extractors
    from transformers import StandardTransformer
    
    def analyze_data_quality():
        """Analyze data quality from extracted and transformed data"""
        
        print("=" * 70)
        print("ETL PIPELINE QUALITY ANALYSIS DEMO")
        print("=" * 70)
        
        # Setup
        source_dir = os.environ['ETL_SOURCE_DIR']
        extractors = create_extractors()
        directory_extractor = DirectoryExtractor(extractors)
        transformer = StandardTransformer()
        
        print(f"📁 Source Directory: {source_dir}")
        print()
        
        # Extract data
        print("PHASE 1: DATA EXTRACTION")
        print("-" * 30)
        
        batch, raw_records = directory_extractor.extract_from_directory(source_dir)
        
        print(f"✅ Extracted {len(raw_records)} records from {len(batch.source_files)} files")
        
        if raw_records:
            # Show sample raw record
            sample = raw_records[0]
            print(f"\n📋 Sample Raw Record:")
            print(f"  Source: {sample.get('source', 'N/A')}")
            print(f"  Title: {sample.get('title', 'N/A')[:50]}...")
            print(f"  Company: {sample.get('company', 'N/A')}")
            print(f"  Technologies: {sample.get('technologies', [])[:3]}")
            print(f"  Location: {sample.get('location', 'N/A')}")
        
        print()
        
        # Transform data
        print("PHASE 2: DATA TRANSFORMATION & QUALITY ANALYSIS")
        print("-" * 50)
        
        offers = []
        quality_scores = []
        tech_counts = {}
        location_counts = {}
        tjm_values = []
        
        for record in raw_records:
            try:
                offer = transformer.transform(record)
                offers.append(offer)
                
                # Collect quality metrics
                if offer.quality_metrics:
                    quality_scores.append(offer.quality_metrics.overall_score)
                
                # Collect technology stats
                for tech in offer.technologies:
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1
                
                # Collect location stats
                if offer.location and offer.location.city:
                    city = offer.location.city
                    location_counts[city] = location_counts.get(city, 0) + 1
                
                # Collect TJM stats
                if offer.tjm and offer.tjm.is_valid():
                    avg_tjm = offer.tjm.get_average()
                    if avg_tjm:
                        tjm_values.append(avg_tjm)
                        
            except Exception as e:
                print(f"⚠️  Transformation error: {e}")
        
        print(f"✅ Transformed {len(offers)} offers successfully")
        
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            min_quality = min(quality_scores)
            max_quality = max(quality_scores)
            
            print(f"\n📊 QUALITY ANALYSIS:")
            print(f"  Average Quality Score: {avg_quality:.2f}")
            print(f"  Quality Range: {min_quality:.2f} - {max_quality:.2f}")
            
            # Quality distribution
            high_quality = sum(1 for s in quality_scores if s >= 0.8)
            medium_quality = sum(1 for s in quality_scores if 0.6 <= s < 0.8)
            low_quality = sum(1 for s in quality_scores if s < 0.6)
            
            print(f"  Quality Distribution:")
            print(f"    🟢 High (≥0.8): {high_quality} ({high_quality/len(offers)*100:.1f}%)")
            print(f"    🟡 Medium (0.6-0.8): {medium_quality} ({medium_quality/len(offers)*100:.1f}%)")
            print(f"    🔴 Low (<0.6): {low_quality} ({low_quality/len(offers)*100:.1f}%)")
        
        if tech_counts:
            print(f"\n🔧 TECHNOLOGY ANALYSIS:")
            sorted_techs = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)
            print(f"  Total Unique Technologies: {len(tech_counts)}")
            print(f"  Top 5 Technologies:")
            for tech, count in sorted_techs[:5]:
                print(f"    {tech}: {count} mentions")
        
        if location_counts:
            print(f"\n📍 LOCATION ANALYSIS:")
            sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
            print(f"  Total Unique Locations: {len(location_counts)}")
            print(f"  Top Locations:")
            for location, count in sorted_locations[:5]:
                print(f"    {location}: {count} offers")
        
        if tjm_values:
            print(f"\n💰 TJM ANALYSIS:")
            avg_tjm = sum(tjm_values) / len(tjm_values)
            min_tjm = min(tjm_values)
            max_tjm = max(tjm_values)
            
            print(f"  Offers with TJM: {len(tjm_values)} / {len(offers)} ({len(tjm_values)/len(offers)*100:.1f}%)")
            print(f"  TJM Range: {min_tjm:.0f}€ - {max_tjm:.0f}€")
            print(f"  Average TJM: {avg_tjm:.0f}€")
            
            # TJM ranges
            ranges = [
                (0, 300, "Entry Level"),
                (300, 500, "Junior"),
                (500, 700, "Confirmé"),
                (700, 1000, "Senior"),
                (1000, float('inf'), "Expert")
            ]
            
            print(f"  TJM Distribution:")
            for min_val, max_val, label in ranges:
                count = sum(1 for v in tjm_values if min_val <= v < max_val)
                if count > 0:
                    percentage = count / len(tjm_values) * 100
                    range_str = f"{min_val}-{max_val if max_val != float('inf') else '+'}€"
                    print(f"    {label} ({range_str}): {count} ({percentage:.1f}%)")
        
        print()
        
        # Show detailed example
        if offers:
            print("PHASE 3: DETAILED OFFER EXAMPLE")
            print("-" * 35)
            
            # Find a high-quality offer
            best_offer = max(offers, key=lambda o: o.quality_metrics.overall_score if o.quality_metrics else 0)
            
            print(f"🏆 BEST QUALITY OFFER (Score: {best_offer.quality_metrics.overall_score:.2f}):")
            print(f"  Title: {best_offer.title}")
            print(f"  Company: {best_offer.company.name if best_offer.company else 'N/A'}")
            print(f"  Technologies: {', '.join(best_offer.technologies[:5])}")
            if best_offer.tjm:
                if best_offer.tjm.min_rate and best_offer.tjm.max_rate:
                    print(f"  TJM: {best_offer.tjm.min_rate:.0f}€ - {best_offer.tjm.max_rate:.0f}€")
                else:
                    print(f"  TJM: {best_offer.tjm.min_rate or best_offer.tjm.max_rate:.0f}€")
            print(f"  Location: {best_offer.location.normalize() if best_offer.location else 'N/A'}")
            print(f"  Remote: {best_offer.remote_policy.value if best_offer.remote_policy else 'N/A'}")
            print(f"  Source: {best_offer.source}")
            
            if best_offer.quality_metrics:
                metrics = best_offer.quality_metrics
                print(f"\n  Quality Breakdown:")
                print(f"    Completeness: {metrics.completeness_score:.2f}")
                print(f"    Accuracy: {metrics.accuracy_score:.2f}")
                print(f"    Consistency: {metrics.consistency_score:.2f}")
                
                if metrics.missing_fields:
                    print(f"    Missing Fields: {', '.join(metrics.missing_fields)}")
        
        print("\n" + "=" * 70)
        print("ETL QUALITY ANALYSIS COMPLETE")
        print("=" * 70)
        
        return {
            "total_records": len(raw_records),
            "total_offers": len(offers),
            "avg_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "technology_count": len(tech_counts),
            "location_count": len(location_counts),
            "tjm_coverage": len(tjm_values) / len(offers) if offers else 0
        }
    
    if __name__ == "__main__":
        analyze_data_quality()

except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
