from os import path
from utils_load import log_activate
from utils_load import db_init, db_connect
from utils_load import data_load, data_convert, data_insert, report_create

MODE_DEBUG = False  # True or False
BASE_DIR = path.abspath(path.dirname(__file__))

APP_DIR = path.join(BASE_DIR, "ovdp")
INST_DIR = path.join(BASE_DIR, "instance")

LOGS_DIR = path.join(INST_DIR, "logs")
if not path.isdir(LOGS_DIR):
    LOGS_DIR = BASE_DIR
DATABASE = path.join(APP_DIR, "auctions.db")

SOURCE_DATA = "https://bank.gov.ua/NBUStatService/v1/statdirectory/ovdp?json"
REPORTS_DIR = path.join(APP_DIR, "static", "reports")
YEARS_AFTER = 2011

if MODE_DEBUG is True:
    DATABASE = path.join(INST_DIR, "auctions.db")
    REPORTS_DIR = INST_DIR


def get_connect(db_file):
    """Get connect to the database."""
    if not path.exists(db_file):
        result = db_init(db_file)
        if result is True:
            logger.info("The database is initialized.")
        else:
            logger.warning("The database is not initialized. Error: '{}'".format(result))
    return db_connect(db_file)


if __name__ == '__main__':
    logger = log_activate(LOGS_DIR, MODE_DEBUG)

    conn = get_connect(DATABASE)
    if conn:
        logger.debug("The connection is successful.")

        total_changes = None
        try:
            data = data_load(SOURCE_DATA)
        except ConnectionError as err_c:
            logger.info("ConnectionError: {}".format(err_c))
        except ValueError as err_v:
            logger.warning("ValueError: {}".format(err_v))
        else:
            data = data_convert(data)
            if data:
                total_changes = data_insert(conn, data)

        if total_changes:
            logger.info("Database updated, new data: {}".format(total_changes))

            val_codes = ['UAH', 'USD', 'EUR']
            result = report_create(conn, REPORTS_DIR, YEARS_AFTER, val_codes)
            logger.info(result)

        conn.close()
