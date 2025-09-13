"""Data models for MSc admission information."""

from dataclasses import dataclass, asdict
from typing import Optional, List
import json


@dataclass
class CourseInfo:
    """Data model for MSc course admission information."""
    
    university: str
    course_name: str
    course_code: Optional[str] = None
    course_features: Optional[str] = None
    course_content: Optional[str] = None
    admission_requirements: Optional[str] = None
    application_deadline: Optional[str] = None
    application_period: Optional[str] = None
    language_of_teaching: Optional[str] = None
    duration: Optional[str] = None
    tuition_fee: Optional[str] = None
    contact_info: Optional[str] = None
    source_url: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class ScrapingResult:
    """Result of scraping operation."""
    
    university: str
    success: bool
    courses: List[CourseInfo]
    error_message: Optional[str] = None
    scraped_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'university': self.university,
            'success': self.success,
            'courses': [course.to_dict() for course in self.courses],
            'error_message': self.error_message,
            'scraped_at': self.scraped_at
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)