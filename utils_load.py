import os
import logging
import logging.config
import sqlite3
import requests
import re


def log_activate(path_to_logs, mode_debug=False):
    logger_on = "application"
    if mode_debug is True:
        logger_on = "debugging"

    log_app = 'app.log'
    log_debug = 'debug.log'
    if os.path.isdir(path_to_logs):
        log_app = os.path.join(path_to_logs, log_app)
        log_debug = os.path.join(path_to_logs, log_debug)

    dictLogConfig = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "level": "WARNING",
            "handlers": [
                "console",
                "logFileRotation"
            ]
        },
        "loggers": {
            "application": {
                "handlers": ["logFileRotation"],
                "level": "INFO",
                "propagate": False
            },
            "debugging": {
                "handlers": [
                    "debug",
                    "logFileDebug"
                ],
                "level": "DEBUG",
                "propagate": False
            }
        },
        "handlers": {
            "debug": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "brief"
            },
            "logFileDebug": {
                "class": "logging.FileHandler",
                "formatter": "verbose",
                "mode": "a",
                "encoding": "utf8",
                "filename": log_debug
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "WARNING",
                "formatter": "brief"
            },
            "logFileRotation": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "verbose",
                "backupCount": 3,
                "maxBytes": 102400,
                "encoding": "utf8",
                "filename": log_app
            }
        },
        "formatters": {
            "verbose": {
                "format": "%(asctime)s - %(name)s - %(levelname)-12s %(message)s",
                "datefmt": '%Y-%m-%d %H:%M:%S'
            },
            "brief": {
                "format": "%(levelname)-10s %(message)s"
            }
        }
    }

    logging.config.dictConfig(dictLogConfig)
    logger = logging.getLogger(logger_on)
    logger.info('*** The logger is activated. ***')

    return logger


def db_init(path_to_db, schema_db):
    try:
        connection = sqlite3.connect(path_to_db)
        connection.executescript(schema_db)
    except sqlite3.DatabaseError as err:
        return str(err)
    else:
        return True


def db_connect(path_to_db):
    return sqlite3.connect(path_to_db)


def db_insert(connection, query, data):
    try:
        connection.execute(query, data)
    except sqlite3.IntegrityError:
        return False
    else:
        return True


def db_select(connection, query, data=None):
    if data:
        return [row for row in connection.execute(query, data)]
    else:
        return [row for row in connection.execute(query)]


def data_load(source_data):
    try:
        request = requests.get(source_data, timeout=5)
    except requests.exceptions.RequestException as err:
        raise ConnectionError(str(err))
    else:
        if request.status_code != 200:
            raise ConnectionError("Connection error. Status code: {}".format(request.status_code))

        try:
            data = request.json()
        except Exception:
            raise ValueError("Error converting data to JSON format.")
        else:
            return data


def check_date(date_string):
    """We check the date and change the format (for strftime) if necessary."""
    if re.search(r'\d\d\d\d-\d\d-\d\d', date_string):
        # 2021-03-24 -> Ok
        return date_string
    if re.search(r'\d\d\d\d\.\d\d\.\d\d', date_string):
        # 2021.03.24 -> 2021-03-24 -> Ok
        temp = date_string.split(".")
        return "-".join(temp)
    if re.search(r'\d\d\.\d\d\.\d\d\d\d', date_string):
        # 24.03.2021 -> 2021-03-24 -> Ok
        temp = date_string.split(".")
        return "-".join(temp[::-1])


def data_convert(data):
    if data[0].get('auctiondate'):
        result = []
        for i in range(len(data)):
            if data[i]['attraction'] > 0:
                auct_num = data[i]['auctionnum']
                date_in = check_date(data[i]['auctiondate'])
                date_out = check_date(data[i]['repaydate'])
                money = data[i]['attraction']
                percent = data[i]['incomelevel']
                val_code = data[i]['valcode'].strip()
                stock_code = data[i]['stockcode'].strip()
                # Collect data in a tuple.
                row_data = (auct_num, date_in, date_out,
                            money, percent, val_code, stock_code)
                result.append(row_data)

        return result


def data_insert(conn, data):
    check_data = "SELECT * FROM auctions WHERE auct_num = ? AND date_in = ?;"
    insert_data = "INSERT INTO auctions (auct_num, date_in, date_out, money, \
                                            percent, val_code, stock_code) \
                                         VALUES (?, ?, ?, ?, ?, ?, ?);"
    PRIMARY_KEY = slice(0, 2)
    total_changes = 0

    for row in data:
        id_exists = db_select(conn, check_data, row[PRIMARY_KEY])
        if not id_exists:
            db_insert(conn, insert_data, row)

    if conn.total_changes:
        conn.commit()
        total_changes = conn.total_changes

    return total_changes


def report_create():
    return "report_create() start..."
