#!/usr/bin/env python
import os
import sys
import shutil
import logging
import tempfile
import operator
import sqlite3

from flask import Flask, jsonify, render_template, request


APP = Flask(__name__)

APP.config.update(dict(
    DATABASE=os.path.join(APP.root_path, 'test.db')
))

def connect_db():
    rv = sqlite3.connect(APP.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

@APP.route('/')
def index():
    # this loads the homepage
    myoptvars = 2
    rv = connect_db()
    c = rv.cursor()

    tabledata = {'name': [], 'email': [], 'multitrack_name': []}

    for row in c.execute('SELECT * FROM tickets'):
        tabledata['name'].append(row[0])
        tabledata['email'].append(row[1])
        tabledata['multitrack_name'].append(row[2])

    x = {
        'date':[u'2012-06-28', u'2012-06-29', u'2012-06-30'],
        'users': [405, 368, 119]
    }
    return render_template('mywebsite.html', x=tabledata)


@APP.route('/api/flufluflu')
def api_flufluflu():
    """
    do the flululu
    """
    # code that does things
    myvar = 'a'
    tralala = 'asdf'
    return jsonify(var1=myvar, var2=tralala)


if __name__ == '__main__':
    APP.run(port=5080, host='0.0.0.0', debug='--debug' in sys.argv)
