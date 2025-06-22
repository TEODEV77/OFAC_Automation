import logging
import sys
from pathlib import Path

def setup_logging():
    """
    Configures logging for the entire application.

    - Creates a 'logs' directory if it does not exist.
    - Logs messages to both a file ('logs/automation.log') and the console (stdout).
    - Sets the log format to include timestamp, log level, logger name, and message.
    - Sets the logging level to INFO for the root logger.
    - Sets WARNING level for noisy third-party libraries (selenium, urllib3, WDM).
    """
    log_directory = Path("logs")
    log_directory.mkdir(exist_ok=True)
    log_file = log_directory / "automation.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Reduce verbosity of third-party libraries
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("WDM").setLevel(logging.WARNING)