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

def format_headers(column_name):
    return column_name.replace("_", " ").title()

# TEMPLATE NAVIGATION----------------------
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
    tickets_headers = get_header('tickets')

    tickets = {}
    for name in tickets_headers:
        tickets[name] = []

    tickets['url']=[]
    for row in cursor:
        for name, item in zip(tickets_headers, row):
            tickets[name].append(item)
        tickets['url'].append('/ticket?id={}'.format(row[0]))

    formatted_tickets_headers = [format_headers(h) for h in tickets_headers]

    return render_template('viewtickets.html', tickets=tickets, 
        db_tickets_headers=tickets_headers, 
        formatted_tickets_headers=formatted_tickets_headers)


@APP.route('/instructions')
def instructions():
    return render_template('instructions.html')

@APP.route('/bandnames')
def band_names():
    return render_template('bandnames.html')

# This is for internal functions, like adding things to the database---------------
@APP.route('/ticket')
def ticket():
    """
    view a single ticket
    """
    ticket_id = request.args.get('id')
    rv = connect_db()
    ticket_status_headers = get_header('tickets')
    ticket_history_headers = get_header('ticket_history')
    multitracks_in_ticket_headers = get_header('multitracks')

    formatted_ticket_status_headers = [format_headers(h) for h in ticket_status_headers]
    formatted_ticket_history_headers = [format_headers(h) for h in ticket_history_headers]
    formatted_multitracks_in_ticket_headers = [format_headers(h) for h in multitracks_in_ticket_headers]
    
    ticket_status_cursor = rv.execute('select * from tickets where ticket_number="{}"'.format(ticket_id))
    ticket_history_cursor = rv.execute('select * from ticket_history where ticket_number="{}"'.format(ticket_id))
    multitracks_cursor = rv.execute('select * from multitracks where ticket_number="{}"'.format(ticket_id))
    
    tickets = fill_table(ticket_status_headers, ticket_status_cursor)
    ticket_history = fill_table(ticket_history_headers, ticket_history_cursor)
    multitracks_in_ticket = fill_table(multitracks_in_ticket_headers, multitracks_cursor)

    multitracks_in_ticket['url']=[]
    multitracks_cursor = rv.execute('select * from multitracks where ticket_number="{}"'.format(ticket_id))
    for row in multitracks_cursor:
        multitracks_in_ticket['url'].append('/multitrack?id={}'.format(row[2]))

    return render_template('ticket.html', ticket_id=ticket_id, 
            db_ticket_status_headers=ticket_status_headers, 
            formatted_ticket_status_headers=formatted_ticket_status_headers, 
            db_ticket_history_headers=ticket_history_headers, 
            formatted_ticket_history_headers=formatted_ticket_history_headers, 
            db_multitracks_in_ticket_headers=multitracks_in_ticket_headers, 
            formatted_multitracks_in_ticket_headers=formatted_multitracks_in_ticket_headers,
            tickets=tickets, 
            ticket_history=ticket_history, 
            multitracks_in_ticket=multitracks_in_ticket)

@APP.route('/multitrack')
def multitrack():
    '''
    view a single multitrack
    '''
    multitrack_id = request.args.get('id')
    rv = connect_db()
    
    multitrack_status_headers = get_header('multitracks')
    multitrack_history_headers = get_header('multitrack_history')
    
    formatted_multitrack_status_headers = [format_headers(h) for h in multitrack_status_headers]
    formatted_multitrack_history_headers = [format_headers(h) for h in multitrack_history_headers]

    multitrack_status_cursor = rv.execute('select * from multitracks where multitrack_id="{}"'.format(multitrack_id))
    multitrack_history_cursor = rv.execute('select * from multitrack_history where multitrack_id="{}"'.format(multitrack_id))

    multitrack = fill_table(multitrack_status_headers, multitrack_status_cursor)
    multitrack_history = fill_table(multitrack_history_headers, multitrack_history_cursor)

    return render_template('multitrack.html', multitrack_id=multitrack_id,
        db_multitrack_status_headers=multitrack_status_headers, 
        formatted_multitrack_status_headers=formatted_multitrack_status_headers,
        db_multitrack_history_headers=multitrack_history_headers,
        formatted_multitrack_history_headers=formatted_multitrack_history_headers,
        multitrack_history=multitrack_history, 
        multitrack_status=multitrack)


if __name__ == '__main__':
    APP.run(port=5080, host='0.0.0.0', debug='--debug' in sys.argv)




