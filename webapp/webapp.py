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
    """
    Creates and connects to an sqlite3 database that will hold the data of tickets and multitracks.

    Returns
    -------
    rv: database
    """
    rv = sqlite3.connect(APP.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def fill_table(headers, cursor):
    """
    Fills a table with given headers.

    Parameters
    ----------
    headers: list of column names
    cursor: database object

    Returns
    -------
    table: dictionary of headers
    """
    table = {}
    for name in headers:
        table[name] = []

    for row in cursor:
        for name, item in zip(headers, row):
            table[name].append(item)

    return table


def get_header(table_name):
    """
    Retrieves headers from a table on the database
    
    Parameters
    ---------
    table_name: string

    Returns
    -------
    column_headers: list
    """
    rv = connect_db()
    cursor = rv.execute('select * from {}'.format(table_name))
    column_headers = list(map(lambda x: x[0], cursor.description))

    return column_headers

def format_headers(column_name):
    """
    Formats headers of tables so underscores are replaced with spaces, and makes first letter of each word uppercase.

    Parameters
    ----------
    column_name: string

    Returns
    -------
    list of strings
    """
    return column_name.replace("_", " ").title()

# TEMPLATE NAVIGATION----------------------
@APP.route('/')
def index():
    """
    Renders home.html template

    Returns
    -------
    'home.html': template
    """
    return render_template('home.html')


@APP.route('/requestrecord')
def request_record():
    """
    Renders requestrecord.html template

    Returns
    -------
    'requestrecord.html': template
    """
    return render_template('requestrecord.html', var1=None, var2=None)


@APP.route('/newticket')
def new_ticket():
    """
    Renders  newticket.html template

    Returns
    -------
    'newticket.html': template
    """
    return render_template('newticket.html', var1=None, var2=None)


@APP.route('/viewtickets')
def view_tickets():
    """
    Renders viewtickets.html template

    Returns
    -------
    'viewtickets.html': renders to a template
    tickets: dictionary
        empty entrys in the tickets table
    db_tickets_headers: list
        headers from the tickets table
    formatted_tickets_headers: list
        formatted headers from tickets table
    """
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
    """
    Renders  instructions.html template

    Returns
    -------
    'instructions.html': template
    """
    return render_template('instructions.html')

@APP.route('/bandnames')
def band_names():
    """
    Renders  bandnames.html template

    Returns
    -------
    'bandnames.html': template
    """
    return render_template('bandnames.html')

# This is for internal functions, like adding things to the database---------------
@APP.route('/ticket')
def ticket():
    """
    Views more information about a single ticket given a ticket ID. 
    Gives info on status of ticket, its history, and multitracks in the ticket.

    Return
    ------
    'ticket.html': rendered template
    ticket_id: int
        requested by the user
    db_ticket_status_headers: list
        headers of ticket status table
    formatted_ticket_status_headers: list
        formatted headers of ticket status table
    db_ticket_history_headers: list
        headers of ticket history table
    formatted_ticket_history_headers: list
        formatted headers of ticket history table 
    db_multitracks_in_ticket_headers: list
        headers of multitracks in ticket table 
    formatted_multitracks_in_ticket_headers: list
        formatted headers of multitracks in ticket tabls
    tickets: dictionary
        content in tickets table
    ticket_history: dictionary
        contents in ticket history table 
    multitracks_in_ticket: dictionary
        contents in multitracks in ticket table

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
    """
    Views more information about a single multitrack within a ticket given a multitrack ID. 
    Gives info on status of multitrack and its history.

    Return
    ------
    'multitrack.html': rendered template
    multitrack_id: int
        requested by the user
    db_ticket_status_headers: list
        headers of ticket status table
    formatted_ticket_status_headers: list
        formatted headers of ticket status table
    db_multitrack_history_headers: list
        headers of multitrack history table
    formatted_multitrack_history_headers: list
        formatted headers of multitrack history table
    multitrack_history: dictionary
        contents in multitrack history table 
    multitrack_status: dictionary
        contents in multitrack status table

    """
   
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

@APP.route('/thankyou')
def requestrecord_api():
    name = request.args.get('name')
    email = request.args.get('email')

    """
    DO FOR EVERYTHING
    collect form information
    create new ticket in database using info
    send email to right people
    redirect to "thank you for submitting form, html file that says thank you"
    """

    # return jsonify(name=name, email=email)
    return render_template('thankyou.html')


@APP.route('/multitrack_info')
def newticket_api():
    """
    DO FOR EVERYTHING
    collect form information
    create new ticket in database using info
    redirect to newticket_multitrack"
    """
    num_multitracks = request.args.get('num')
    return render_template('newticket_multitracks.html', num_multitracks=int(num_multitracks))


if __name__ == '__main__':
    APP.run(port=5080, host='0.0.0.0', debug='--debug' in sys.argv)




