"""Mock scraper for demonstration purposes when real websites are not accessible."""

from typing import List, Optional
from datetime import datetime

from base_scraper import BaseScraper
from models import CourseInfo


class MockHKUScraper(BaseScraper):
    """Mock HKU scraper that returns sample data for demonstration."""
    
    def __init__(self):
        super().__init__(
            university_name="University of Hong Kong (HKU)",
            base_url="https://www.hku.hk"
        )
    
    def get_msc_course_urls(self) -> List[str]:
        """Return mock URLs for demonstration."""
        return [
            "https://www.hku.hk/msc/computer-science",
            "https://www.hku.hk/msc/data-science",
            "https://www.hku.hk/msc/engineering",
            "https://www.hku.hk/msc/business-analytics",
            "https://www.hku.hk/msc/finance"
        ]
    
    def extract_course_info(self, course_url: str) -> Optional[CourseInfo]:
        """Return mock course information."""
        # Mock data based on URL
        mock_courses = {
            "computer-science": CourseInfo(
                university=self.university_name,
                course_name="Master of Science in Computer Science",
                course_code="MSc(CompSc)",
                course_features="This program provides advanced training in computer science theories and practical skills. Students will gain expertise in algorithms, software engineering, artificial intelligence, and data structures.",
                course_content="Core courses include: Advanced Algorithms, Machine Learning, Software Engineering, Database Systems, Computer Networks, Artificial Intelligence, and Thesis Research.",
                admission_requirements="Bachelor's degree in Computer Science, Engineering, Mathematics, or related field with minimum GPA 3.0. TOEFL/IELTS required for non-native English speakers.",
                application_deadline="March 31, 2024",
                application_period="November 1, 2023 - March 31, 2024",
                language_of_teaching="English",
                duration="1 year full-time or 2 years part-time",
                tuition_fee="HK$180,000 (full program)",
                contact_info="Email: admissions@cs.hku.hk | Phone: +852 3917-2660",
                source_url=course_url
            ),
            "data-science": CourseInfo(
                university=self.university_name,
                course_name="Master of Science in Data Science",
                course_code="MSc(DataSci)",
                course_features="Interdisciplinary program combining statistics, computer science, and domain expertise. Prepares students for data scientist roles in various industries.",
                course_content="Statistical Methods, Machine Learning, Data Mining, Big Data Analytics, Data Visualization, Python/R Programming, Database Management.",
                admission_requirements="Bachelor's degree in Mathematics, Statistics, Computer Science, Engineering, or related quantitative field. Strong mathematical background required.",
                application_deadline="April 30, 2024",
                application_period="December 1, 2023 - April 30, 2024",
                language_of_teaching="English",
                duration="1.5 years full-time",
                tuition_fee="HK$200,000 (full program)",
                contact_info="Email: msc-datasci@hku.hk | Phone: +852 3917-4803",
                source_url=course_url
            ),
            "engineering": CourseInfo(
                university=self.university_name,
                course_name="Master of Science in Engineering",
                course_code="MSc(Eng)",
                course_features="Advanced engineering program with specializations in Civil, Electrical, Mechanical, and Industrial Engineering. Focus on innovation and practical applications.",
                course_content="Engineering Mathematics, Advanced Design, Project Management, Sustainable Engineering, Materials Science, and specialized tracks.",
                admission_requirements="Bachelor's degree in Engineering or related field. Professional experience preferred but not required.",
                application_deadline="May 31, 2024",
                application_period="January 1, 2024 - May 31, 2024",
                language_of_teaching="English",
                duration="1 year full-time or 2 years part-time",
                tuition_fee="HK$160,000 (full program)",
                contact_info="Email: msc-eng@hku.hk | Phone: +852 3917-7054",
                source_url=course_url
            ),
            "business-analytics": CourseInfo(
                university=self.university_name,
                course_name="Master of Science in Business Analytics",
                course_code="MSc(BA)",
                course_features="Combines business acumen with analytical skills. Covers predictive analytics, optimization, and strategic decision-making for business applications.",
                course_content="Business Intelligence, Predictive Modeling, Operations Research, Marketing Analytics, Financial Analytics, Supply Chain Analytics.",
                admission_requirements="Bachelor's degree in Business, Economics, Engineering, Mathematics, or related field. Work experience preferred.",
                application_deadline="June 30, 2024",
                application_period="February 1, 2024 - June 30, 2024",
                language_of_teaching="English",
                duration="1 year full-time",
                tuition_fee="HK$220,000 (full program)",
                contact_info="Email: msc-ba@business.hku.hk | Phone: +852 3917-5678",
                source_url=course_url
            ),
            "finance": CourseInfo(
                university=self.university_name,
                course_name="Master of Science in Finance",
                course_code="MSc(Fin)",
                course_features="Rigorous quantitative finance program preparing students for careers in investment banking, asset management, and financial analysis.",
                course_content="Financial Markets, Derivatives, Portfolio Management, Risk Management, Financial Modeling, Corporate Finance, Investment Analysis.",
                admission_requirements="Bachelor's degree in Finance, Economics, Mathematics, Engineering, or related field. Strong quantitative skills required.",
                application_deadline="March 15, 2024",
                application_period="October 1, 2023 - March 15, 2024",
                language_of_teaching="English",
                duration="1 year full-time",
                tuition_fee="HK$250,000 (full program)",
                contact_info="Email: msc-finance@hku.hk | Phone: +852 3917-8901",
                source_url=course_url
            )
        }
        
        # Extract program name from URL
        for key, course in mock_courses.items():
            if key in course_url:
                return course
        
        return None


class MockCUHKScraper(BaseScraper):
    """Mock CUHK scraper for demonstration."""
    
    def __init__(self):
        super().__init__(
            university_name="Chinese University of Hong Kong (CUHK)",
            base_url="https://www.cuhk.edu.hk"
        )
    
    def get_msc_course_urls(self) -> List[str]:
        """Return mock URLs for demonstration."""
        return [
            "https://www.cuhk.edu.hk/msc/information-engineering",
            "https://www.cuhk.edu.hk/msc/business-analytics",
            "https://www.cuhk.edu.hk/msc/mathematics"
        ]
    
    def extract_course_info(self, course_url: str) -> Optional[CourseInfo]:
        """Return mock course information for CUHK."""
        mock_courses = {
            "information-engineering": CourseInfo(
                university=self.university_name,
                course_name="Master of Science in Information Engineering",
                course_code="MSc(IE)",
                course_features="Advanced program in information systems, telecommunications, and network engineering with strong industry connections.",
                course_content="Network Protocols, Information Security, Wireless Communications, Internet Technologies, Data Communications.",
                admission_requirements="Bachelor's degree in Engineering, Computer Science, or related field. Minimum GPA 3.0 required.",
                application_deadline="April 15, 2024",
                language_of_teaching="English and Cantonese",
                duration="1 year full-time or 2 years part-time",
                tuition_fee="HK$170,000 (full program)",
                contact_info="Email: ie-admission@cuhk.edu.hk",
                source_url=course_url
            ),
            "business-analytics": CourseInfo(
                university=self.university_name,
                course_name="Master of Science in Business Analytics",
                course_code="MSc(BA)",
                course_features="Interdisciplinary program focusing on data-driven business decision making and analytics applications.",
                course_content="Statistical Analysis, Business Intelligence, Data Mining, Marketing Analytics, Operations Analytics.",
                admission_requirements="Bachelor's degree with strong quantitative background. GMAT/GRE preferred.",
                application_deadline="May 1, 2024",
                language_of_teaching="English",
                duration="1 year full-time",
                tuition_fee="HK$190,000 (full program)",
                contact_info="Email: ba-program@cuhk.edu.hk",
                source_url=course_url
            ),
            "mathematics": CourseInfo(
                university=self.university_name,
                course_name="Master of Science in Mathematics",
                course_code="MSc(Math)",
                course_features="Research-oriented program in pure and applied mathematics with flexible specialization options.",
                course_content="Advanced Calculus, Linear Algebra, Mathematical Analysis, Probability Theory, Applied Mathematics.",
                admission_requirements="Bachelor's degree in Mathematics or related field with strong mathematical background.",
                application_deadline="February 28, 2024",
                language_of_teaching="English",
                duration="1.5 years full-time",
                tuition_fee="HK$140,000 (full program)",
                contact_info="Email: math-grad@cuhk.edu.hk",
                source_url=course_url
            )
        }
        
        for key, course in mock_courses.items():
            if key in course_url:
                return course
        
        return None