from ovdp import app
from flask import render_template, request, abort
from flask import g
import sqlite3
from ovdp.utils_app import convert_to_int, paginate


current_year = 2019
years = [x for x in range(2012, current_year)]


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(app.config['DATABASE'])
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    query = "SELECT * FROM auctions \
                      WHERE CAST(strftime('%Y', date_in) as INTEGER) > 2011 \
                      ORDER BY date_in DESC, auct_num DESC;"
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
    items = cursor.fetchmany(2)
    return render_template("index.html", auctions=items)


@app.route('/stats')
def stats():
    return render_template("stats.html", show_year=current_year, list_year=years)


@app.route('/year')
@app.route('/year/<int:num_year>')
def show_year(num_year=None):
    if num_year:
        if num_year not in years:
            abort(404)
    else:
        num_year = current_year

    return render_template("year.html", show_year=num_year, list_year=years)


@app.route('/auctions')
def auctions():
    query = "SELECT * FROM auctions \
                      WHERE CAST(strftime('%Y', date_in) as INTEGER) > 2011 \
                      ORDER BY date_in DESC, auct_num DESC;"

    get_year = request.args.get('year')
    if not get_year:
        year = None
    else:
        year = convert_to_int(get_year)
        if not year:
            abort(400)
        if year not in years:
            abort(404)

        query = "SELECT * FROM auctions \
                          WHERE CAST(strftime('%Y', date_in) as INTEGER) = {} \
                          ORDER BY date_in DESC, auct_num DESC;".format(year)

    get_page = request.args.get('page')
    if not get_page:
        page = 1
    else:
        page = convert_to_int(get_page)
        if not page:
            abort(400)

    item_qty = 16
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query)
        item_all = cursor.fetchall()
        result = paginate(item_all, item_qty, page)
    except ConnectionError:
        abort(500)
    except ValueError:
        abort(404)
    except Exception:
        abort(400)
    else:
        return render_template("auctions.html", year=year, list_year=years, **result)


@app.errorhandler(400)
def bad_request(error):
    return render_template('400.html'), 400


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500


@app.context_processor
def inject_year():
    return dict(menu_year=current_year)


@app.template_filter()
def money_format(value):
    return format(round(value), ',d')
