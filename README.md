# Infojobs Scraper

A modern Python web scraper for Infojobs.net that allows you to search and collect job offers data.

## Features

- Search for jobs using keywords
- Collect detailed information about job offers:
  - Position
  - Company name
  - Company valuation
  - City
  - Country
  - Contract type
  - Salary
  - Minimum experience required
  - Job URL
- Save results to CSV files
- Progress bars for tracking scraping progress
- Error handling and retry mechanisms
- Respects website's robots.txt

## Requirements

- Python 3.8+
- Chrome browser installed
- Required Python packages (install using `pip install -r requirements.txt`):
  - selenium
  - beautifulsoup4
  - pandas
  - tqdm
  - webdriver-manager
  - requests

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd infojobs-scraper
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper with default settings:

```bash
python infojobs_scraper.py
```

The script will:
1. Ask for search keywords
2. Open Chrome browser
3. Wait for you to solve the CAPTCHA and apply any desired filters
4. Start scraping job offers
5. Save results to a CSV file in the `results` directory

### Using as a Module

```python
from infojobs_scraper import InfojobsScraper

# Initialize scraper
scraper = InfojobsScraper(headless=False)  # Set headless=True for background operation

# Search and scrape jobs
output_file = scraper.scrape_jobs(
    keywords="Data Scientist",
    output_dir="my_results"
)

# Check results
if output_file:
    print(f"Results saved to: {output_file}")
```

## Output

The scraper saves results in CSV format with the following columns:
- position: Job title
- company: Company name
- company_valuation: Company rating (1-100)
- city: Job location city
- country: Job location country
- contract_type: Type of contract
- salary: Salary information
- min_exp: Minimum experience required
- url: Link to the job offer

## Notes

- The scraper includes delays between requests to be respectful to the website
- You may need to solve a CAPTCHA when starting a new search
- Some job offers might not have all information available
- The scraper is for educational purposes only. Please respect Infojobs.net's terms of service and robots.txt

## License

This project is licensed under the MIT License - see the LICENSE file for details.
