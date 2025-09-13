"""Base scraper class for university admission information."""

import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import logging
import time
from abc import ABC, abstractmethod

from models import CourseInfo, ScrapingResult


class BaseScraper(ABC):
    """Base class for university website scrapers."""
    
    def __init__(self, university_name: str, base_url: str):
        self.university_name = university_name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logger = logging.getLogger(f"{__name__}.{university_name}")
    
    def fetch_page(self, url: str, timeout: int = 30) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    @abstractmethod
    def get_msc_course_urls(self) -> List[str]:
        """Get list of URLs for all MSc courses."""
        pass
    
    @abstractmethod
    def extract_course_info(self, course_url: str) -> Optional[CourseInfo]:
        """Extract course information from a course page."""
        pass
    
    def scrape_all_courses(self, delay: float = 1.0) -> ScrapingResult:
        """Scrape all MSc courses for this university."""
        from datetime import datetime
        
        self.logger.info(f"Starting scraping for {self.university_name}")
        courses = []
        error_message = None
        
        try:
            course_urls = self.get_msc_course_urls()
            self.logger.info(f"Found {len(course_urls)} course URLs")
            
            for i, url in enumerate(course_urls):
                self.logger.info(f"Scraping course {i+1}/{len(course_urls)}: {url}")
                
                course_info = self.extract_course_info(url)
                if course_info:
                    courses.append(course_info)
                
                # Add delay to be respectful to the server
                if delay > 0 and i < len(course_urls) - 1:
                    time.sleep(delay)
            
            success = True
            self.logger.info(f"Successfully scraped {len(courses)} courses")
            
        except Exception as e:
            success = False
            error_message = str(e)
            self.logger.error(f"Scraping failed: {e}")
        
        return ScrapingResult(
            university=self.university_name,
            success=success,
            courses=courses,
            error_message=error_message,
            scraped_at=datetime.now().isoformat()
        )