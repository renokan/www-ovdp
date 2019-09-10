from ovdp import app
from flask import g
import sqlite3
from ovdp.queries import dict_q


def get_query(name_query):
    query = dict_q.get(name_query)
    if not query:
        query = " "  # get_query('name_query').format()  <-- str.format()
    return query


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(app.config['DATABASE'])
    return g.sqlite_db


def db_years(query):
    conn = sqlite3.connect(app.config['DATABASE'])
    years = [row[0] for row in conn.execute(query)]
    conn.close()

    if years:
        year = years.pop()
        return (year, years)

    years = [x for x in range(2012, 2019)]
    return (2019, years)


def convert_to_int(string):
    if string.isdigit():
        return int(string)


def paginate(item_all, item_qty, page=1):
    if not item_all:
        raise ConnectionError

    pages = len(item_all[::item_qty])
    if page < 1 or page > pages:
        raise ValueError

    page_prev = None
    page_next = None
    slice_start = None
    slice_end = None
    if pages != 1:
        if page == 1:
            page_next = page + 1
            slice_end = page * item_qty
        elif page == pages:
            page_prev = page - 1
            slice_start = ((page - 1) * item_qty)
        else:
            page_prev = page - 1
            page_next = page + 1
            slice_start = ((page - 1) * item_qty)
            slice_end = (page * item_qty)
    data = item_all[slice_start:slice_end]

    output = {'page': page, 'pages': pages,
              'previous': page_prev, 'next': page_next,
              'data': data}

    return output
