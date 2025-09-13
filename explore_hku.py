#!/usr/bin/env python3
"""Test script to explore HKU website structure for MSc programs."""

import requests
from bs4 import BeautifulSoup
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models import CourseInfo

def explore_hku():
    """Explore HKU website to understand structure."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    # Start with HKU main graduate admission page
    base_urls = [
        "https://www.hku.hk/prospective/graduate/",
        "https://www.hku.hk/acadinfo/taught/",
        "https://www.graduate.hku.hk/prospective-students/taught-postgraduate-admissions/"
    ]
    
    for url in base_urls:
        print(f"\n=== Exploring {url} ===")
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for links to MSc programs
            links = soup.find_all('a', href=True)
            msc_links = []
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                
                if ('msc' in text or 'master' in text or 'graduate' in text) and href:
                    if href.startswith('/'):
                        href = f"https://www.hku.hk{href}"
                    elif not href.startswith('http'):
                        href = f"{url.rstrip('/')}/{href}"
                    msc_links.append((text, href))
            
            print(f"Found {len(msc_links)} potential MSc-related links:")
            for text, href in msc_links[:10]:  # Show first 10
                print(f"  - {text}: {href}")
                
        except Exception as e:
            print(f"Error exploring {url}: {e}")

if __name__ == "__main__":
    explore_hku()