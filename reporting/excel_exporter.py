import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from config import settings

logger = logging.getLogger(__name__)

def create_incomplete_records_report(records: list):
    """
    Generate an Excel report from a list of incomplete records.

    Args:
        records (list): List of dictionaries, each representing a record.
    Returns:
        None
    """
    if not records:
        logger.info("No records with 'Incomplete Information' found. Skipping report generation.")
        return

    try:
        # Create DataFrame from records
        data_frame = pd.DataFrame(records)

        # Generate dynamic filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"Incomplete_Records_Report_{timestamp}.xlsx"
        file_path = Path(settings.REPORTS_DIR) / file_name

        # Select and rename columns for clarity
        data_frame = data_frame[['idPersona', 'nombrePersona', 'pais', 'estadoTransaccion']]
        data_frame.columns = ['Person ID', 'Person Name', 'Country', 'Transaction Status']

        # Save DataFrame to Excel
        data_frame.to_excel(file_path, index=False, engine='openpyxl')

        # Adjust column widths using openpyxl
        from openpyxl import load_workbook
        work_book = load_workbook(file_path)
        work_sheet = work_book.active

        work_sheet.column_dimensions['B'].width = 35  # Person Name
        work_sheet.column_dimensions['C'].width = 15  # Country
        work_sheet.column_dimensions['D'].width = 25  # Transaction Status

        work_book.save(file_path)
        logger.info(f"Successfully generated Excel report: {file_path}")

    except Exception as e:
        logger.error(f"Failed to create the Excel report: {e}")