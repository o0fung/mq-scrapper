"""HKU (University of Hong Kong) website scraper."""

import re
from typing import List, Optional
from urllib.parse import urljoin, urlparse

from base_scraper import BaseScraper
from models import CourseInfo


class HKUScraper(BaseScraper):
    """Scraper for University of Hong Kong (HKU) MSc programs."""
    
    def __init__(self):
        super().__init__(
            university_name="University of Hong Kong (HKU)",
            base_url="https://www.hku.hk"
        )
        # Common HKU URLs for graduate programs
        self.graduate_urls = [
            "https://www.graduate.hku.hk/prospective-students/taught-postgraduate-admissions/",
            "https://www.hku.hk/acadinfo/taught/",
            "https://www.hku.hk/prospective/graduate/"
        ]
    
    def get_msc_course_urls(self) -> List[str]:
        """Get list of URLs for all MSc courses at HKU."""
        course_urls = []
        
        for url in self.graduate_urls:
            soup = self.fetch_page(url)
            if not soup:
                continue
            
            # Look for links to MSc programs
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True).lower()
                
                # Filter for MSc/Master's programs
                if self._is_msc_link(text, href):
                    full_url = urljoin(url, href)
                    if full_url not in course_urls:
                        course_urls.append(full_url)
        
        # Also try to find faculty-specific pages
        faculty_urls = self._get_faculty_graduate_pages()
        for faculty_url in faculty_urls:
            soup = self.fetch_page(faculty_url)
            if not soup:
                continue
                
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True).lower()
                
                if self._is_msc_link(text, href):
                    full_url = urljoin(faculty_url, href)
                    if full_url not in course_urls:
                        course_urls.append(full_url)
        
        return course_urls
    
    def _is_msc_link(self, text: str, href: str) -> bool:
        """Check if a link is likely for an MSc program."""
        if not href:
            return False
            
        text = text.lower()
        href = href.lower()
        
        # Keywords that indicate MSc programs
        msc_keywords = [
            'msc', 'master of science', 'masters', 'postgraduate',
            'graduate', 'taught masters', 'coursework'
        ]
        
        # Check text content
        text_match = any(keyword in text for keyword in msc_keywords)
        
        # Check URL patterns common in university sites
        url_patterns = [
            r'msc',
            r'master',
            r'postgrad',
            r'graduate',
            r'taught'
        ]
        url_match = any(re.search(pattern, href) for pattern in url_patterns)
        
        return text_match or url_match
    
    def _get_faculty_graduate_pages(self) -> List[str]:
        """Get URLs for faculty-specific graduate program pages."""
        # Common HKU faculty structure
        faculties = [
            'architecture', 'arts', 'business', 'dentistry', 'education',
            'engineering', 'law', 'medicine', 'science', 'social-sciences'
        ]
        
        faculty_urls = []
        for faculty in faculties:
            # Try common URL patterns
            patterns = [
                f"https://www.{faculty}.hku.hk/graduate/",
                f"https://www.{faculty}.hku.hk/prospective/postgraduate/",
                f"https://www.hku.hk/{faculty}/graduate/",
                f"https://www.hku.hk/f/{faculty}/postgraduate/"
            ]
            faculty_urls.extend(patterns)
        
        return faculty_urls
    
    def extract_course_info(self, course_url: str) -> Optional[CourseInfo]:
        """Extract course information from an HKU course page."""
        soup = self.fetch_page(course_url)
        if not soup:
            return None
        
        try:
            # Extract course name (common patterns in HKU pages)
            course_name = self._extract_course_name(soup)
            if not course_name:
                return None
            
            # Extract other information
            course_code = self._extract_course_code(soup)
            course_features = self._extract_course_features(soup)
            course_content = self._extract_course_content(soup)
            admission_requirements = self._extract_admission_requirements(soup)
            application_deadline = self._extract_application_deadline(soup)
            application_period = self._extract_application_period(soup)
            language_of_teaching = self._extract_language_of_teaching(soup)
            duration = self._extract_duration(soup)
            tuition_fee = self._extract_tuition_fee(soup)
            contact_info = self._extract_contact_info(soup)
            
            return CourseInfo(
                university=self.university_name,
                course_name=course_name,
                course_code=course_code,
                course_features=course_features,
                course_content=course_content,
                admission_requirements=admission_requirements,
                application_deadline=application_deadline,
                application_period=application_period,
                language_of_teaching=language_of_teaching,
                duration=duration,
                tuition_fee=tuition_fee,
                contact_info=contact_info,
                source_url=course_url
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting course info from {course_url}: {e}")
            return None
    
    def _extract_course_name(self, soup) -> Optional[str]:
        """Extract course name from page."""
        # Try different selectors commonly used for course titles
        selectors = [
            'h1',
            '.course-title',
            '.program-title',
            '.page-title',
            'title',
            '.main-title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and len(text) > 5:  # Basic validation
                    return text
        
        return None
    
    def _extract_course_code(self, soup) -> Optional[str]:
        """Extract course code."""
        # Look for patterns like "MSc(CompSc)" or "COMP 7900"
        text = soup.get_text()
        patterns = [
            r'MSc\([^)]+\)',
            r'[A-Z]{3,4}\s+\d{4}',
            r'Course Code:\s*([A-Z0-9\s\(\)]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        
        return None
    
    def _extract_course_features(self, soup) -> Optional[str]:
        """Extract course features/description."""
        # Look for sections with course description
        selectors = [
            '.course-description',
            '.program-overview',
            '.course-overview',
            '.course-features',
            '.highlights'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Try to find paragraphs that might contain description
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 100 and any(keyword in text.lower() for keyword in 
                                       ['program', 'course', 'designed', 'students']):
                return text
        
        return None
    
    def _extract_course_content(self, soup) -> Optional[str]:
        """Extract course content/curriculum."""
        selectors = [
            '.curriculum',
            '.course-content',
            '.syllabus',
            '.modules',
            '.subjects'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    def _extract_admission_requirements(self, soup) -> Optional[str]:
        """Extract admission requirements."""
        selectors = [
            '.admission-requirements',
            '.entry-requirements',
            '.requirements',
            '.eligibility'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Look for text patterns
        text = soup.get_text()
        if 'admission requirements' in text.lower():
            # Find the section with admission requirements
            lines = text.split('\n')
            in_requirements = False
            requirements = []
            
            for line in lines:
                line = line.strip()
                if 'admission requirements' in line.lower():
                    in_requirements = True
                    continue
                elif in_requirements:
                    if line and not line.lower().startswith(('application', 'fee', 'contact')):
                        requirements.append(line)
                    elif len(requirements) > 3:  # Got enough context
                        break
            
            if requirements:
                return '\n'.join(requirements)
        
        return None
    
    def _extract_application_deadline(self, soup) -> Optional[str]:
        """Extract application deadline."""
        text = soup.get_text()
        patterns = [
            r'deadline[:\s]*([^.\n]+)',
            r'apply by[:\s]*([^.\n]+)',
            r'application closes[:\s]*([^.\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_application_period(self, soup) -> Optional[str]:
        """Extract application period."""
        text = soup.get_text()
        patterns = [
            r'application period[:\s]*([^.\n]+)',
            r'applications open[:\s]*([^.\n]+)',
            r'application dates[:\s]*([^.\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_language_of_teaching(self, soup) -> Optional[str]:
        """Extract language of teaching."""
        text = soup.get_text()
        patterns = [
            r'language of (?:instruction|teaching)[:\s]*([^.\n]+)',
            r'taught in[:\s]*([^.\n]+)',
            r'medium of instruction[:\s]*([^.\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Default assumption for HKU
        return "English"
    
    def _extract_duration(self, soup) -> Optional[str]:
        """Extract program duration."""
        text = soup.get_text()
        patterns = [
            r'duration[:\s]*([^.\n]+)',
            r'(?:full|part).?time[:\s]*([^.\n]+)',
            r'(\d+)\s*(?:year|month)s?',
            r'program length[:\s]*([^.\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_tuition_fee(self, soup) -> Optional[str]:
        """Extract tuition fee information."""
        text = soup.get_text()
        patterns = [
            r'tuition[:\s]*([^.\n]+)',
            r'fee[s]?[:\s]*([^.\n]+)',
            r'HK\$[0-9,]+',
            r'cost[:\s]*([^.\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    def _extract_contact_info(self, soup) -> Optional[str]:
        """Extract contact information."""
        selectors = [
            '.contact',
            '.contact-info',
            '.enquiry',
            '.enquiries'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Look for email patterns
        text = soup.get_text()
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        
        if emails:
            return f"Email: {', '.join(emails)}"
        
        return None