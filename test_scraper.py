#!/usr/bin/env python3
"""Test script to verify the scraper implementation works correctly."""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models import CourseInfo, ScrapingResult
from data_exporter import DataExporter


def test_models():
    """Test the data models."""
    print("Testing data models...")
    
    # Create a sample course
    course = CourseInfo(
        university="Test University",
        course_name="Master of Science in Computer Science",
        course_code="MSc(CompSc)",
        course_features="Advanced computer science program",
        course_content="Algorithms, Machine Learning, Software Engineering",
        admission_requirements="Bachelor's degree in Computer Science or related field",
        application_deadline="March 31, 2024",
        language_of_teaching="English",
        duration="1 year full-time",
        tuition_fee="HK$180,000",
        source_url="https://example.com/msc-cs"
    )
    
    print(f"Course created: {course.course_name}")
    print(f"JSON representation: {course.to_json()}")
    
    # Create a scraping result
    result = ScrapingResult(
        university="Test University",
        success=True,
        courses=[course],
        scraped_at=datetime.now().isoformat()
    )
    
    print(f"Result created: {result.university} - Success: {result.success}")
    return [result]


def test_data_export(results):
    """Test data export functionality."""
    print("\nTesting data export...")
    
    exporter = DataExporter()
    
    # Test JSON export
    json_file = exporter.export_json(results, "test_data.json")
    print(f"JSON exported to: {json_file}")
    
    # Test CSV export
    csv_file = exporter.export_csv(results, "test_data.csv")
    print(f"CSV exported to: {csv_file}")
    
    # Test summary report
    report = exporter.generate_summary_report(results)
    print(f"\nSummary Report:\n{report}")


def test_config():
    """Test configuration management."""
    print("\nTesting configuration...")
    
    try:
        from config import config
        print(f"Scraping delay: {config.scraping_delay}")
        print(f"Request timeout: {config.request_timeout}")
        print(f"Log level: {config.log_level}")
        print(f"Output directory: {config.output_directory}")
        print(f"Enabled universities: {config.get_enabled_universities()}")
    except Exception as e:
        print(f"Configuration test failed: {e}")


def main():
    """Run all tests."""
    print("Running scraper tests...\n")
    
    # Test models and data export
    results = test_models()
    test_data_export(results)
    test_config()
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    main()