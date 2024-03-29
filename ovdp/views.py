from ovdp import app
from flask import request, url_for, g
from flask import render_template, abort, redirect
from ovdp.utils_app import get_query, get_db, db_years
from ovdp.utils_app import convert_to_int, paginate

YEARS_AFTER = 2011

query = get_query('years').format(YEARS_AFTER)
YEAR, YEARS = db_years(query)


@app.route('/')
def index():
    query = get_query('auctions').format(YEARS_AFTER)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
    data = cursor.fetchmany(2)

    return render_template("index.html", auctions=data)


@app.route('/stats')
def stats():
    return render_template("stats.html")


@app.route('/year')
@app.route('/year/<int:year>')
def show_year(year=None):
    if not year:
        year = YEAR
    else:
        if year == YEAR:
            return redirect(url_for('show_year'), code=307)
        if year not in YEARS:
            abort(404)

    return render_template("year.html", year=year)


@app.route('/auctions')
def auctions():
    query = get_query('auctions').format(YEARS_AFTER)

    get_year = request.args.get('year')
    if not get_year:
        year = None
    else:
        year = convert_to_int(get_year)
        if not year:
            abort(400)
        if year not in YEARS:
            abort(404)

        query = get_query('auct_year').format(year)

    get_page = request.args.get('page')
    if not get_page:
        page = 1
    else:
        page = convert_to_int(get_page)
        if not page:
            abort(400)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    qty = 16
    try:
        result = paginate(data, qty, page)
    except ConnectionError:
        abort(500)
    except ValueError:
        abort(404)
    except Exception:
        abort(400)
    else:
        return render_template("auctions.html", year=year, **result)


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
def inject_years():
    return dict(year_in_menu=YEAR, years=YEARS)


@app.template_filter()
def money_format(value):
    return format(round(value), ',d')


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
