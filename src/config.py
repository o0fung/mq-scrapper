"""Configuration management for the scraper."""

import json
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file {self.config_file} not found")
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'scraping.delay')."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_enabled_universities(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration for enabled universities."""
        universities = self.get('universities', {})
        return {
            key: config for key, config in universities.items() 
            if config.get('enabled', False)
        }
    
    @property
    def scraping_delay(self) -> float:
        """Get delay between requests."""
        return self.get('scraping.delay_between_requests', 1.0)
    
    @property
    def request_timeout(self) -> int:
        """Get request timeout."""
        return self.get('scraping.request_timeout', 30)
    
    @property
    def max_retries(self) -> int:
        """Get maximum retries."""
        return self.get('scraping.max_retries', 3)
    
    @property
    def user_agent(self) -> str:
        """Get user agent string."""
        return self.get('scraping.user_agent', 
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.get('logging.level', 'INFO')
    
    @property
    def output_directory(self) -> str:
        """Get output directory."""
        return self.get('export.output_directory', 'output')
    
    @property
    def export_formats(self) -> list:
        """Get export formats."""
        return self.get('export.formats', ['json', 'csv'])


# Global configuration instance
config = Config()