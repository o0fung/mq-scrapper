"""Data export utilities for scraping results."""

import json
import csv
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
import logging

from models import CourseInfo, ScrapingResult


class DataExporter:
    """Handles exporting scraping results to various formats."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def export_json(self, results: List[ScrapingResult], filename: str = None) -> str:
        """Export results to JSON format."""
        if filename is None:
            filename = "hk_msc_admission_data.json"
        
        filepath = self.output_dir / filename
        
        # Convert results to dictionary format
        export_data = {
            'metadata': {
                'total_universities': len(results),
                'total_courses': sum(len(result.courses) for result in results if result.success),
                'export_timestamp': pd.Timestamp.now().isoformat()
            },
            'universities': [result.to_dict() for result in results]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Exported JSON data to {filepath}")
        return str(filepath)
    
    def export_csv(self, results: List[ScrapingResult], filename: str = None) -> str:
        """Export results to CSV format."""
        if filename is None:
            filename = "hk_msc_admission_data.csv"
        
        filepath = self.output_dir / filename
        
        # Flatten the data for CSV export
        rows = []
        for result in results:
            if result.success:
                for course in result.courses:
                    row = course.to_dict()
                    row['scraped_at'] = result.scraped_at
                    rows.append(row)
            else:
                # Add a row indicating the failure
                rows.append({
                    'university': result.university,
                    'course_name': f"SCRAPING_FAILED: {result.error_message}",
                    'scraped_at': result.scraped_at
                })
        
        if not rows:
            self.logger.warning("No data to export to CSV")
            return str(filepath)
        
        # Write CSV
        fieldnames = list(rows[0].keys())
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        self.logger.info(f"Exported CSV data to {filepath}")
        return str(filepath)
    
    def export_excel(self, results: List[ScrapingResult], filename: str = None) -> str:
        """Export results to Excel format with multiple sheets."""
        if filename is None:
            filename = "hk_msc_admission_data.xlsx"
        
        filepath = self.output_dir / filename
        
        # Create separate sheets for each university
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = []
            all_courses = []
            
            for result in results:
                summary_data.append({
                    'University': result.university,
                    'Success': result.success,
                    'Courses Found': len(result.courses) if result.success else 0,
                    'Error Message': result.error_message,
                    'Scraped At': result.scraped_at
                })
                
                if result.success:
                    for course in result.courses:
                        course_dict = course.to_dict()
                        course_dict['scraped_at'] = result.scraped_at
                        all_courses.append(course_dict)
            
            # Write summary sheet
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Write all courses sheet
            if all_courses:
                all_courses_df = pd.DataFrame(all_courses)
                all_courses_df.to_excel(writer, sheet_name='All Courses', index=False)
            
            # Write individual university sheets
            for result in results:
                if result.success and result.courses:
                    courses_data = [course.to_dict() for course in result.courses]
                    df = pd.DataFrame(courses_data)
                    
                    # Clean university name for sheet name
                    sheet_name = result.university.replace('(', '').replace(')', '').replace(' ', '_')
                    sheet_name = sheet_name[:31]  # Excel sheet name limit
                    
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        self.logger.info(f"Exported Excel data to {filepath}")
        return str(filepath)
    
    def export_all_formats(self, results: List[ScrapingResult], base_filename: str = None) -> Dict[str, str]:
        """Export results to all supported formats."""
        if base_filename is None:
            base_filename = "hk_msc_admission_data"
        
        export_files = {}
        
        try:
            export_files['json'] = self.export_json(results, f"{base_filename}.json")
        except Exception as e:
            self.logger.error(f"Failed to export JSON: {e}")
        
        try:
            export_files['csv'] = self.export_csv(results, f"{base_filename}.csv")
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {e}")
        
        try:
            export_files['excel'] = self.export_excel(results, f"{base_filename}.xlsx")
        except Exception as e:
            self.logger.error(f"Failed to export Excel: {e}")
        
        return export_files
    
    def generate_summary_report(self, results: List[ScrapingResult]) -> str:
        """Generate a text summary report."""
        report_lines = ["Hong Kong MSc Admission Data Scraping Report", "=" * 50, ""]
        
        total_universities = len(results)
        successful_scrapes = sum(1 for result in results if result.success)
        total_courses = sum(len(result.courses) for result in results if result.success)
        
        report_lines.extend([
            f"Total Universities Attempted: {total_universities}",
            f"Successful Scrapes: {successful_scrapes}",
            f"Total Courses Found: {total_courses}",
            ""
        ])
        
        # Per-university summary
        report_lines.append("Per-University Results:")
        report_lines.append("-" * 30)
        
        for result in results:
            status = "SUCCESS" if result.success else "FAILED"
            course_count = len(result.courses) if result.success else 0
            
            report_lines.append(f"{result.university}: {status} ({course_count} courses)")
            if not result.success and result.error_message:
                report_lines.append(f"  Error: {result.error_message}")
        
        report_lines.append("")
        
        # Course statistics
        if total_courses > 0:
            report_lines.append("Course Statistics:")
            report_lines.append("-" * 20)
            
            # Count courses by university
            for result in results:
                if result.success and result.courses:
                    report_lines.append(f"{result.university}: {len(result.courses)} courses")
        
        report_content = "\n".join(report_lines)
        
        # Save report to file
        report_file = self.output_dir / "scraping_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"Generated summary report: {report_file}")
        return report_content