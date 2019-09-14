import os
from datetime import datetime
import logging
import logging.config
import sqlite3
import requests
import re
import pygal
from pygal.style import Style


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
    logger.debug('*** The logger is activated. ***')

    return logger


def get_connect(logger, db_file):
    """Get connect to the database."""
    if not os.path.isfile(db_file):
        result = db_init(db_file)
        if result is True:
            logger.info("The database is initialized.")
        else:
            logger.warning("The database is not initialized. Error: '{}'".format(result))

    return db_connect(db_file)


def db_init(file_db):
    schema = """
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
    try:
        connection = sqlite3.connect(file_db)
        connection.executescript(schema)
    except sqlite3.DatabaseError as err:
        return str(err)
    else:
        return True


def db_connect(file_db):
    return sqlite3.connect(file_db)


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
            raise ConnectionError("Request status_code {}".format(request.status_code))

        try:
            data = request.json()
        except Exception:
            raise ValueError("Error converting data to JSON format.")
        else:
            return data


def check_date(date_string):
    """We check the date and change the format (for strftime) if necessary."""
    if re.search(r'\d{4}-\d\d-\d\d', date_string):
        # 2021-03-24 -> Ok
        return date_string
    if re.search(r'\d{4}\.\d\d\.\d\d', date_string):
        # 2021.03.24 -> 2021-03-24 -> Ok
        temp = date_string.split(".")
        return "-".join(temp)
    if re.search(r'\d\d\.[0-1][0-9]\.\d{4}\b', date_string):
        # 24.03.2021 -> 2021-03-24 -> Ok
        temp = date_string.split(".")
        return "-".join(temp[::-1])


def data_convert(data):
    if data[0].get('auctiondate'):
        result = []
        now = datetime.now()
        now_year = now.year
        for i in range(len(data)):
            if data[i]['attraction'] > 0:
                auct_num = data[i]['auctionnum']
                date_in = check_date(data[i]['auctiondate'])
                date_out = check_date(data[i]['repaydate'])
                money = data[i]['attraction']
                percent = data[i]['incomelevel']
                val_code = data[i]['valcode'].strip()
                stock_code = data[i]['stockcode'].strip()

                if not date_in or not date_out:
                    raise ValueError("Invalid date format.")

                auction_year = int(date_in.split("-")[0])  # '2021-12-31'
                if auction_year > now_year:
                    continue

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


def inout_get_data(conn, val_code, column_inout, year=None):
    query_y = "SELECT CAST(strftime('%m', {0}) as INTEGER) as month, SUM(money) \
                            FROM auctions \
                            WHERE val_code = ? AND  \
                                  CAST(strftime('%Y', {0}) as INTEGER) = ? \
                            GROUP BY month \
                            ORDER BY month ASC;".format(column_inout)
    query_s = "SELECT CAST(strftime('%Y', {}) as INTEGER) as year, SUM(money) \
                                    FROM auctions \
                                    WHERE val_code = ? \
                                    GROUP BY year \
                                    ORDER BY year ASC;".format(column_inout)

    if year:
        return db_select(conn, query_y, (val_code, year))
    else:
        return db_select(conn, query_s, (val_code, ))


def inout_convert_data(period, data, scale_size, round_size=2):
    """We fill in the missing data in the period with values ​​of 0."""
    result = []
    for date_x in period:
        money = 0
        for row in data:
            date_y, money_origin = row
            if date_y == date_x:
                money = round((money_origin / scale_size), round_size)
        result.append(money)

    return result


def inout_get_period(data_1, data_2, years_after):
    data = data_1 + data_2
    years = list(set([x[0] for x in data if x[0] > years_after]))
    years.sort()

    return years


def create_svg(title, period, data_in, data_out, file_svg):
    custom_style = Style(colors=("#0d00d6", "#ff0000"), background="#ffffff")

    svg_chart = pygal.Bar(style=custom_style)
    svg_chart.title = title
    svg_chart.x_labels = map(str, period)
    svg_chart.add('In', data_in)
    svg_chart.add('Out', data_out)
    svg_chart.render_to_file(file_svg)


def report_create(conn, path_to, years_after, val_codes):
    years = "SELECT DISTINCT CAST(strftime('%Y', date_in) as INTEGER) as year \
                                            FROM auctions \
                                            ORDER BY year ASC;"
    years = [row[0] for row in conn.execute(years)]
    year = years.pop()

    for val_code in val_codes:
        if val_code == "UAH":
            scale = {"title": "billion", "size": 1000000000}
        else:
            scale = {"title": "million", "size": 1000000}

        # Stats: create report in SVG format.
        title = "Currency {}, {}".format(val_code.upper(), scale["title"])
        file_svg = "report_stat_{}.svg"
        file_svg = os.path.join(path_to, file_svg.format(val_code.lower()))
        data_in = inout_get_data(conn, val_code, 'date_in')
        data_out = inout_get_data(conn, val_code, 'date_out')
        years = inout_get_period(data_in, data_out, years_after)
        data_in = inout_convert_data(years, data_in, scale["size"])
        data_out = inout_convert_data(years, data_out, scale["size"])
        create_svg(title, years, data_in, data_out, file_svg)

        # Year: create report in SVG format.
        title = "Year: {} - Currency {}, {}".format(year, val_code.upper(), scale["title"])
        file_svg = "report_{}_{}.svg"
        file_svg = os.path.join(path_to, file_svg.format(year, val_code.lower()))
        data_in = inout_get_data(conn, val_code, 'date_in', year)
        data_out = inout_get_data(conn, val_code, 'date_out', year)
        months = [x for x in range(1, 13)]
        data_in = inout_convert_data(months, data_in, scale["size"])
        data_out = inout_convert_data(months, data_out, scale["size"])
        create_svg(title, months, data_in, data_out, file_svg)
