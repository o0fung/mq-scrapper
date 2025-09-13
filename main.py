#!/usr/bin/env python3
"""Main script to scrape MSc admission information from Hong Kong universities."""

import logging
import sys
import os
import argparse
from pathlib import Path
from typing import List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models import ScrapingResult
from hku_scraper import HKUScraper
from data_exporter import DataExporter
from config import config
from mock_scrapers import MockHKUScraper, MockCUHKScraper


def setup_logging(log_level: str = None) -> None:
    """Setup logging configuration."""
    if log_level is None:
        log_level = config.log_level
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    handlers = []
    if config.get('logging.log_to_file', True):
        handlers.append(logging.FileHandler(log_dir / "scraper.log"))
    if config.get('logging.log_to_console', True):
        handlers.append(logging.StreamHandler(sys.stdout))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def get_scrapers(use_mock: bool = False) -> List:
    """Get list of scrapers based on configuration."""
    scrapers = []
    
    if use_mock:
        # Use mock scrapers for demonstration
        scrapers.extend([
            MockHKUScraper(),
            MockCUHKScraper()
        ])
    else:
        # Use real scrapers based on configuration
        enabled_universities = config.get_enabled_universities()
        
        for uni_key, uni_config in enabled_universities.items():
            if uni_key == 'hku':
                scrapers.append(HKUScraper())
            # Add other real scrapers here as they are implemented
            # elif uni_key == 'cuhk':
            #     scrapers.append(CUHKScraper())
    
    return scrapers


def main():
    """Main function to orchestrate the scraping process."""
    parser = argparse.ArgumentParser(
        description="Scrape MSc admission information from Hong Kong universities"
    )
    parser.add_argument(
        '--mock', 
        action='store_true', 
        help='Use mock data for demonstration (when websites are not accessible)'
    )
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
        help='Set logging level'
    )
    parser.add_argument(
        '--output-format', 
        choices=['json', 'csv', 'excel', 'all'], 
        default='all',
        help='Choose output format'
    )
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    if args.mock:
        logger.info("Starting Hong Kong MSc admission information scraping (MOCK MODE)")
    else:
        logger.info("Starting Hong Kong MSc admission information scraping")
    
    # Initialize scrapers
    scrapers = get_scrapers(use_mock=args.mock)
    
    if not scrapers:
        logger.error("No scrapers configured or enabled. Check config.json")
        return
    
    logger.info(f"Initialized {len(scrapers)} scrapers")
    
    results: List[ScrapingResult] = []
    
    # Run scraping for each university
    for scraper in scrapers:
        logger.info(f"Starting scraping for {scraper.university_name}")
        try:
            result = scraper.scrape_all_courses(delay=config.scraping_delay)
            results.append(result)
            
            if result.success:
                logger.info(f"Successfully scraped {len(result.courses)} courses from {scraper.university_name}")
            else:
                logger.error(f"Failed to scrape {scraper.university_name}: {result.error_message}")
                
        except Exception as e:
            logger.error(f"Unexpected error scraping {scraper.university_name}: {e}")
            # Create a failed result
            from datetime import datetime
            failed_result = ScrapingResult(
                university=scraper.university_name,
                success=False,
                courses=[],
                error_message=str(e),
                scraped_at=datetime.now().isoformat()
            )
            results.append(failed_result)
    
    # Export results
    logger.info("Exporting results")
    exporter = DataExporter(config.output_directory)
    
    try:
        if args.output_format == 'all':
            export_files = exporter.export_all_formats(results)
        else:
            export_files = {}
            if args.output_format == 'json':
                export_files['json'] = exporter.export_json(results)
            elif args.output_format == 'csv':
                export_files['csv'] = exporter.export_csv(results)
            elif args.output_format == 'excel':
                export_files['excel'] = exporter.export_excel(results)
        
        logger.info("Exported data to the following files:")
        for format_name, filepath in export_files.items():
            logger.info(f"  {format_name.upper()}: {filepath}")
        
        # Generate summary report
        if config.get('export.generate_summary', True):
            report = exporter.generate_summary_report(results)
            print("\n" + report)
        
    except Exception as e:
        logger.error(f"Failed to export results: {e}")
    
    # Print final summary
    total_courses = sum(len(result.courses) for result in results if result.success)
    successful_universities = sum(1 for result in results if result.success)
    
    logger.info(f"Scraping completed: {successful_universities}/{len(results)} universities successful, {total_courses} total courses found")


if __name__ == "__main__":
    main()