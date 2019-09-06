import os
import sqlite3


def log_activate(path_to_logs, mode_debug=False):
    import logging
    import logging.config

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
