import logging
from config import settings, logging_config
from database.db_manager import DatabaseManager
from scraping.ofac_scraper import OfacScraper
from reporting.excel_exporter import create_incomplete_records_report

# Setup logging as the first step
logging_config.setup_logging()
logger = logging.getLogger(__name__)

def categorize_persons(all_persons: list) -> tuple:
    """
    Categorizes persons into three groups:
    - search_queue: Persons with complete and valid data.
    - incomplete_records: Persons missing address or country.
    - no_master_records: Persons missing a master record.
    Returns a tuple of (search_queue, incomplete_records, no_master_records).
    """
    search_queue = []
    incomplete_records = []
    no_master_records = []

    for person in all_persons:
        if person['idMaestra'] is None:
            no_master_records.append(person)
        elif not person['direccion'] or not person['pais']:
            incomplete_records.append(person)
        else:
            search_queue.append(person)
    
    logger.info(
        f"Categorization complete: {len(search_queue)} to search, "
        f"{len(incomplete_records)} incomplete, "
        f"{len(no_master_records)} without master record."
    )
    return search_queue, incomplete_records, no_master_records

def process_pre_checks(db_manager: DatabaseManager, incomplete: list, no_master: list):
    """
    Handles persons who failed pre-checks (incomplete or missing master record).
    Inserts their status into the database in bulk.
    """
    bulk_data = []

    for person in incomplete:
        record = (
            person['idPersona'],
            person['nombrePersona'],
            person['pais'],
            None,
            settings.STATUS_INCOMPLETE
        )
        bulk_data.append(record)

    for person in no_master:
        record = (
            person['idPersona'],
            person['nombrePersona'],
            None,
            None,
            settings.STATUS_NO_MASTER_RECORD
        )
        bulk_data.append(record)
    
    if bulk_data:
        logger.info(f"Performing bulk insert for {len(bulk_data)} pre-checked records.")
        db_manager.insert_results_bulk(bulk_data)

def run_ofac_searches(db_manager: DatabaseManager, search_queue: list):
    """
    Runs OFAC searches for all persons in the search queue.
    Handles result insertion and screenshot capture for positive matches.
    """
    if not search_queue:
        logger.info("Search queue is empty. No OFAC checks to perform.")
        return

    try:
        scraper = OfacScraper()
    except Exception as e:
        logger.error(f"Could not start the OFAC scraper. Aborting search process. Error: {e}")
        return

    for person in search_queue:
        person_id = person['idPersona']
        logger.info(f"Processing person ID: {person_id}, Name: {person['nombrePersona']}")
        
        result_count = scraper.search_person(
            name=person['nombrePersona'],
            address=person['direccion'],
            country=person['pais']
        )
        
        if result_count > -1:
            status = settings.STATUS_OK
            db_manager.insert_single_result(person, result_count, status)
            if result_count > 0:
                scraper.take_screenshot(person_id)
        else:
            status = settings.STATUS_ERROR
            db_manager.insert_single_result(person, None, status)

        scraper.reset_search_form()

    scraper.close()

def generate_final_reports(db_manager: DatabaseManager):
    """
    Fetches data and generates all required final reports.
    """
    logger.info("Starting final report generation...")
    incomplete_records = db_manager.fetch_incomplete_records_for_report()
    create_incomplete_records_report(incomplete_records)
    logger.info("Final report generation finished.")

def main():
    """
    Main function to orchestrate the entire OFAC background check automation process.
    Steps:
    1. Connect to the database and fetch persons to process.
    2. Categorize persons and handle pre-check failures.
    3. Run OFAC searches for valid records.
    4. Generate final reports.
    """
    logger.info("--- OFAC Background Check Automation Started ---")
    db_manager = None
    try:
        db_manager = DatabaseManager()
        all_persons = db_manager.fetch_persons_to_process()
        if not all_persons:
            logger.info("No persons found with the 'aConsultar' flag set to 'SI'.")
            return

        search_queue, incomplete, no_master = categorize_persons(all_persons)
        process_pre_checks(db_manager, incomplete, no_master)
        run_ofac_searches(db_manager, search_queue)
        generate_final_reports(db_manager)

    except Exception as e:
        logger.critical(f"A critical error occurred in the main process: {e}", exc_info=True)
    finally:
        if db_manager:
            db_manager.disconnect()
        logger.info("--- OFAC Background Check Automation Finished ---")

if __name__ == "__main__":
    main()