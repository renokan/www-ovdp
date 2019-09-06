from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('ovdp.default_settings')
app.config.from_pyfile('local_settings.py', silent=True)

from ovdp import views
