# Hong Kong MSc Admission Scraper

This project is designed to automatically map, search, and extract useful information regarding admission packages for all MSc courses offered by universities in Hong Kong. The scraper targets specific details such as course features, content, admission requirements, application deadlines, and the language of instruction.

## Features

- **Comprehensive Data Extraction**: Extracts course features, content, admission requirements, application deadlines, language of teaching, tuition fees, duration, and contact information
- **Multiple Universities**: Supports all major Hong Kong universities (HKU, CUHK, HKUST, CityU, PolyU, HKBU, Lingnan, EdUHK)
- **Multiple Export Formats**: Exports data to JSON, CSV, and Excel formats
- **Configurable**: Easy-to-use configuration file for customizing scraping behavior
- **Respectful Scraping**: Implements delays and proper headers to be respectful to university websites
- **Error Handling**: Robust error handling with detailed logging
- **Mock Mode**: Includes mock data for testing and demonstration purposes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/o0fung/hk-msc-admission-scrapper.git
cd hk-msc-admission-scrapper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper with mock data (for demonstration):
```bash
python main.py --mock
```

Run the scraper with real data:
```bash
python main.py
```

### Advanced Usage

Choose specific output format:
```bash
python main.py --mock --output-format json
python main.py --mock --output-format csv
python main.py --mock --output-format excel
```

Set logging level:
```bash
python main.py --mock --log-level DEBUG
```

### Configuration

Edit `config.json` to customize:
- Enable/disable specific universities
- Adjust scraping delays and timeouts
- Configure output formats and directories
- Set logging preferences

Example configuration:
```json
{
  "scraping": {
    "delay_between_requests": 1.0,
    "request_timeout": 30,
    "max_retries": 3
  },
  "universities": {
    "hku": {
      "enabled": true,
      "name": "University of Hong Kong (HKU)",
      "base_url": "https://www.hku.hk"
    }
  }
}
```

## Output

The scraper generates several output files:

1. **JSON Format** (`hk_msc_admission_data.json`): Structured data with metadata
2. **CSV Format** (`hk_msc_admission_data.csv`): Flat table format for analysis
3. **Excel Format** (`hk_msc_admission_data.xlsx`): Multi-sheet workbook with summary and per-university data
4. **Summary Report** (`scraping_report.txt`): Human-readable summary of scraping results

### Sample Output Structure

Each course record includes:
- University name
- Course name and code
- Course features and content
- Admission requirements
- Application deadline and period
- Language of teaching
- Duration and tuition fee
- Contact information
- Source URL

## Project Structure

```
├── src/
│   ├── models.py           # Data models for course information
│   ├── base_scraper.py     # Base scraper class
│   ├── hku_scraper.py      # HKU-specific scraper
│   ├── mock_scrapers.py    # Mock scrapers for testing
│   ├── data_exporter.py    # Data export utilities
│   └── config.py           # Configuration management
├── main.py                 # Main scraper script
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
├── test_scraper.py         # Test script
└── README.md               # This file
```

## Supported Universities

- ✅ University of Hong Kong (HKU) - Mock implementation ready
- ✅ Chinese University of Hong Kong (CUHK) - Mock implementation ready
- 🔄 Hong Kong University of Science and Technology (HKUST) - Planned
- 🔄 City University of Hong Kong (CityU) - Planned
- 🔄 Hong Kong Polytechnic University (PolyU) - Planned
- 🔄 Hong Kong Baptist University (HKBU) - Planned
- 🔄 Lingnan University - Planned
- 🔄 Education University of Hong Kong (EdUHK) - Planned

## Development

### Adding New Universities

1. Create a new scraper class inheriting from `BaseScraper`
2. Implement `get_msc_course_urls()` and `extract_course_info()` methods
3. Add the university configuration to `config.json`
4. Update the scraper factory in `main.py`

### Running Tests

```bash
python test_scraper.py
```

## Logging

Logs are saved to `logs/scraper.log` and also displayed in the console. The logging level can be configured in `config.json` or via command line arguments.

## Ethical Considerations

This scraper is designed to be respectful to university websites:
- Implements delays between requests
- Uses appropriate user agent headers
- Respects robots.txt when applicable
- Only extracts publicly available information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes. Please ensure you comply with the terms of service of the websites you are scraping and respect their robots.txt files.
