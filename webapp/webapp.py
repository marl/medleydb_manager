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
    DATABASE=os.path.join(APP.root_path, 'static', 'ticketmanager.db')
))


def connect_db():
    rv = sqlite3.connect(APP.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def fill_table(headers, cursor):
    table = {}
    for name in headers:
        table[name] = []

    for row in cursor:
        for name, item in zip(headers, row):
            table[name].append(item)

    return table


def get_header(table_name):
    rv = connect_db()
    cursor = rv.execute('select * from {}'.format(table_name))
    column_headers = list(map(lambda x: x[0], cursor.description))

    return column_headers


@APP.route('/')
def index():
    # this loads the homepage
    return render_template('home.html')


@APP.route('/requestrecord')
def request_record():
    return render_template('requestrecord.html', var1=None, var2=None)


@APP.route('/newticket')
def new_ticket():
    return render_template('newticket.html', var1=None, var2=None)


@APP.route('/viewtickets')
def view_tickets():
    rv = connect_db()
    cursor = rv.execute('select * from tickets')
    column_headers = get_header('tickets')

    tickets = {}
    for name in column_headers:
        tickets[name] = []
    tickets['url']=[]

    for row in cursor:
        for name, item in zip(column_headers, row):
            tickets[name].append(item)
        tickets['url'].append('/ticket?id={}'.format(row[0]))

    return render_template('viewtickets.html', tickets=tickets, column_headers=column_headers)


@APP.route('/instructions')
def instructions():
    return render_template('instructions.html')

@APP.route('/bandnames')
def band_names():
    return render_template('bandnames.html')

# This is for internal functions, like adding things to the database
@APP.route('/ticket')
def ticket():
    """
    view a single ticket
    """
    # code that does things
    ticket_id = request.args.get('id')
    rv = connect_db()
    current_status_headers = get_header('tickets')
    ticket_history_headers = get_header('ticket_history')
    multitracks_in_ticket_headers = get_header('multitracks')
    
    current_status = rv.execute('select * from tickets where ticket_number="{}"'.format(ticket_id))
    ticket_history = rv.execute('select * from ticket_history where ticket_number="{}"'.format(ticket_id))
    multitracks_in_ticket = rv.execute('select * from multitracks where ticket_number="{}"'.format(ticket_id))
    
    tickets = fill_table(current_status_headers, current_status)
    ticket_history = fill_table(ticket_history_headers, ticket_history)
    multitracks_in_ticket = fill_table(multitracks_in_ticket_headers, multitracks_in_ticket)
    print tickets
    return render_template('ticket.html', ticket_id=ticket_id, current_status_headers=current_status_headers, 
                           ticket_history_headers=ticket_history_headers, multitracks_in_ticket_headers=multitracks_in_ticket_headers,
                           current_status=tickets, ticket_history=ticket_history, multitracks_in_ticket=multitracks_in_ticket)


if __name__ == '__main__':
    APP.run(port=5080, host='0.0.0.0', debug='--debug' in sys.argv)
