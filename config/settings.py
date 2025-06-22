import os
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Load environment variables from .env file
# -----------------------------------------------------------------------------
load_dotenv()

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# -----------------------------------------------------------------------------
# OFAC Configuration
# -----------------------------------------------------------------------------
OFAC_URL = "https://sanctionssearch.ofac.treas.gov/"

# -----------------------------------------------------------------------------
# Database Table Names
# -----------------------------------------------------------------------------
PERSONS_TABLE = '"Personas"'
MASTER_DETAIL_TABLE = '"MaestraDetallePersonas"'
RESULTS_TABLE = '"Resultadosuser9886"'

# -----------------------------------------------------------------------------
# Directory Paths
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure required directories exist
SCREENSHOTS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# -----------------------------------------------------------------------------
# Process Constants
# -----------------------------------------------------------------------------
PROCESS_FLAG = "Si"
STATUS_OK = "OK"
STATUS_ERROR = "NOK"
STATUS_INCOMPLETE = "Información incompleta"
STATUS_NO_MASTER_RECORD = "No cruza con maestra"

"""
Settings Module Documentation
----------------------------

This module centralizes configuration for the OFAC application.

Sections:
- Environment Variables: Loaded from a .env file for sensitive data.
- Database Configuration: Connection parameters for the main database.
- OFAC Configuration: URL for the OFAC sanctions search.
- Table Names: Centralized table names for database operations.
- Directory Paths: Paths for storing screenshots and reports, created if missing.
- Process Constants: Standardized status and flag values for process control.

Usage:
Import this module wherever configuration values are needed.
"""