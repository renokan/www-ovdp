from os import path

basedir = path.abspath(path.dirname(__file__))

DEBUG = False
TESTING = False
SECRET_KEY = 'The secret_key is set in the config local_settings.py :)'
DATABASE = path.join(basedir, 'auctions.db')
