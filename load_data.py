import requests
import pygal
import os
from utils_load import log_activate
from utils_load import db_init, db_connect, db_insert, db_select

MODE_DEBUG = True  # True or False
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
APP_DIR = os.path.join(BASE_DIR, "ovdp")
INST_DIR = os.path.join(BASE_DIR, "instance")

LOGS_DIR = os.path.join(INST_DIR, "logs")
if not os.path.isdir(LOGS_DIR):
    LOGS_DIR = BASE_DIR
DATABASE = os.path.join(APP_DIR, "auctions.db")
if MODE_DEBUG is True:
    DATABASE = os.path.join(INST_DIR, "auctions.db")
SOURCE_DATA = "https://bank.gov.ua/NBUStatService/v1/statdirectory/ovdp?json"
REPORTS_DIR = os.path.join(APP_DIR, "static", "reports")


def get_connect(db_file):
    """Get connect to the database."""
    db_schema = """
        CREATE TABLE IF NOT EXISTS auctions (
            auct_num    integer not NULL,
            date_in     text not NULL,
            date_out    text not NULL,
            money       real not NULL,
            percent     real not NULL,
            val_code    text not NULL,
            stock_code  text not NULL,
            PRIMARY KEY (auct_num, date_in)
        );
    """
    if not os.path.exists(db_file):
        result = db_init(db_file, db_schema)
        if result is True:
            logger.info("The database is initialized.")
        else:
            logger.warning("The database is not initialized. Error: '{}'".format(result))
    return db_connect(db_file)


if __name__ == '__main__':
    logger = log_activate(LOGS_DIR, MODE_DEBUG)

    conn = get_connect(DATABASE)
    if conn:
        logger.info("Connect OK")
        conn.close()

    # for x in range(50):
    #     logger.debug('This is a debug message')
    #     logger.info('This is an info message')
    #     logger.warning('This is a warning message')
    #     logger.error('This is an error message')
    #     logger.critical('Тест This is a critical message')
