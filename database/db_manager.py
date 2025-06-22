import logging
import psycopg2
from psycopg2.extras import execute_values
from config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Handles all database connections and operations for the OFAC application.

    Responsibilities:
    - Establish and close database connections.
    - Fetch persons to process.
    - Insert OFAC search results (bulk and single).
    - Fetch incomplete records for reporting.
    """

    def __init__(self):
        """
        Initializes the database connection using settings from the config module.
        Raises:
            psycopg2.OperationalError: If the connection cannot be established.
        """
        self.conn = None
        self.cursor = None
        try:
            self.conn = psycopg2.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                dbname=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD
            )
            self.cursor = self.conn.cursor()
            logger.info("Database connection established successfully.")
        except psycopg2.OperationalError as e:
            logger.error(f"Could not connect to the database: {e}")
            raise

    def fetch_persons_to_process(self) -> list:
        """
        Fetches all persons marked for processing, joining with master details.

        Returns:
            list: List of dictionaries with person and master detail data.
        """
        query = f"""
            SELECT
                p."idPersona",
                p."nombrePersona",
                m."idPersona" as "idMaestra",
                m."direccion",
                m."pais"
            FROM
                {settings.PERSONS_TABLE} p
            LEFT JOIN
                {settings.MASTER_DETAIL_TABLE} m ON p."idPersona" = m."idPersona"
            WHERE
                p."aConsultar" = %s;
        """
        try:
            self.cursor.execute(query, (settings.PROCESS_FLAG,))
            columns = [column_description[0] for column_description in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch persons to process: {e}")
            return []

    def insert_results_bulk(self, results_data: list):
        """
        Inserts multiple OFAC search result records in a single transaction.

        Args:
            results_data (list): List of tuples with result data.
        """
        if not results_data:
            return

        query = f"""
            INSERT INTO {settings.RESULTS_TABLE}
                ("idPersona", "nombrePersona", "pais", "cantidadDeResultados", "estadoTransaccion")
            VALUES %s;
        """
        try:
            execute_values(self.cursor, query, results_data)
            self.conn.commit()
            logger.info(f"Successfully bulk-inserted {len(results_data)} records.")
        except Exception as e:
            logger.error(f"Failed to bulk-insert results: {e}")
            self.conn.rollback()

    def insert_single_result(self, person_data: dict, result_count: int, status: str):
        """
        Inserts a single OFAC search result record.

        Args:
            person_data (dict): Person data dictionary.
            result_count (int): Number of OFAC results.
            status (str): Transaction status.
        """
        query = f"""
            INSERT INTO {settings.RESULTS_TABLE}
                ("idPersona", "nombrePersona", "pais", "cantidadDeResultados", "estadoTransaccion")
            VALUES (%s, %s, %s, %s, %s);
        """
        try:
            params = (
                person_data['idPersona'],
                person_data['nombrePersona'],
                person_data['pais'],
                result_count,
                status
            )
            self.cursor.execute(query, params)
            self.conn.commit()
            logger.info(f"Inserted result for person ID {person_data['idPersona']} with status '{status}'.")
        except Exception as e:
            logger.error(f"Failed to insert single result for person ID {person_data['idPersona']}: {e}")
            self.conn.rollback()

    def fetch_incomplete_records_for_report(self) -> list:
        """
        Fetches all records from the results table marked as 'Información incompleta'.

        Returns:
            list: List of dictionaries with incomplete record data.
        """
        query = f"""
            SELECT
                "idPersona",
                "nombrePersona",
                "pais",
                "estadoTransaccion"
            FROM
                {settings.RESULTS_TABLE}
            WHERE
                "estadoTransaccion" = %s;
        """
        try:
            self.cursor.execute(query, (settings.STATUS_INCOMPLETE,))
            columns = [column_description[0] for column_description in self.cursor.description]
            records = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            logger.info(f"Fetched {len(records)} incomplete records for Excel report.")
            return records
        except Exception as e:
            logger.error(f"Failed to fetch incomplete records for report: {e}")
            return []

    def disconnect(self):
        """
        Closes the database connection and cursor.
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")