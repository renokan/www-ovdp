from os import path

basedir = path.abspath(path.dirname(__file__))

DEBUG = False
TESTING = False
SECRET_KEY = 'SECRET KEY'
DATABASE = path.join(basedir, 'auctions.db')
