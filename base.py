# encoding: utf-8

from flask import Flask
from flask import render_template
from flask_wtf.csrf import CsrfProtect

app = Flask(__name__)

app.config.from_pyfile('config.cfg', silent=True)

csrf = CsrfProtect(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

import login
import voting
import sudo