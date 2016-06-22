#!/usr/bin/env python
import os
import sys
import shutil
import logging
import tempfile
import operator
import sqlite3

from flask import Flask, jsonify, render_template, request, redirect


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
    rv = connect_db()
    c = rv.cursor()

    tickets = {'name': [], 'email': [], 'multitrack_name': []}

    for row in c.execute('SELECT * FROM tickets'):
        tickets['name'].append(row[0])
        tickets['email'].append(row[1])
        tickets['multitrack_name'].append(row[2])

    return render_template('home.html', tickets=tickets)


@APP.route('/newticket')
def new_ticket():
    return render_template('newticket.html', var1=None, var2=None)


@APP.route('/viewtickets')
def view_tickets():
    return render_template('viewtickets.html')


@APP.route('/instructions')
def instructions():
    return render_template('instructions.html')

# This is for internal functions, like adding things to the database
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
