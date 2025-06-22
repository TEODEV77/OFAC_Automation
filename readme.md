# OFAC Background Check Automation

## Overview

This project is an automated solution for performing background checks against the OFAC (Office of Foreign Assets Control) sanctions list. It is designed to process a list of individuals, check their details against the OFAC list using automated web scraping, and generate comprehensive reports based on the results.

### Main Workflow

1. **Initialization:** Sets up logging and connects to the database.
2. **Fetch Records:** Retrieves all persons flagged for OFAC processing.
3. **Categorization:** Divides persons into:
   - Persons with complete and valid data (search queue)
   - Incomplete records (missing address or country)
   - Records missing master data
4. **Pre-check Processing:** Handles and logs incomplete or missing records, updating their status in the database.
5. **OFAC Search:** For each valid record, uses Selenium to submit data to the OFAC sanctions search platform and parse the results.
6. **Result Handling:** Inserts results into the database; takes screenshots for positive matches.
7. **Report Generation:** Produces Excel reports summarizing the process and highlighting incomplete records.
8. **Cleanup:** Closes all database and browser connections safely.

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Google Chrome (for Selenium headless browser)
- ChromeDriver (automatically managed via `webdriver_manager`)
- Required Python packages (see below)

### Setup

1. **Clone the repository:**
   ```bash
   git clone git@github.com:TEODEV77/OFAC_Automation.git
   cd OFAC_Automation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   - Create a `.env` file in the root directory with your database credentials and other sensitive settings, as referenced in `config/settings.py`.

4. **Database setup:**
   - Ensure your database contains the tables specified in the configuration.
   - Table names and structure should match those expected by the application.

## Usage

To run the complete OFAC background check workflow, execute:

```bash
python main.py
```

- The script will log its progress and create reports and screenshots in configured directories.

## Configuration

- All configuration (database, OFAC URL, directories, status constants, etc.) is centralized in `config/settings.py`.
- Update the `.env` file and settings as needed for your environment.

## Key Modules

- **main.py:** Orchestrates the entire process.
- **config/settings.py:** Centralized configuration.
- **database/db_manager.py:** Handles all database operations.
- **scraping/ofac_scraper.py:** Automates OFAC platform interactions using Selenium.
- **reporting/excel_exporter.py:** Generates Excel reports of the results.

## Logging & Error Handling

- All operations are logged for traceability (`logging` module).
- Errors are handled gracefully with clear messages in logs.

## Author

Developed by [TEODEV77](https://github.com/TEODEV77)


