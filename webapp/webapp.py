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


@APP.route('/newmultitrack')
def new_multitrack():
    # current_multitrack = 
    num_multitracks = request.args.get('num')
    return render_template('newticket_multitracks.html', current_multitrack=current_multitrack, num_multitracks=int(num_multitracks))


@APP.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')


@APP.route('/api/requestrecord')
def requestrecord_api():
    your_name = request.args.get('your_name')
    your_email = request.args.get('your_email')
    you = request.args.get('you')
    contact_name = request.args.get('contact_name')
    contact_email = request.args.get('contact_email')
    record_date1 = request.args.get('record_date1')
    record_date2 = request.args.get('record_date2')
    record_date3 = request.args.get('record_date3')
    hours_needed = request.args.get('hours_needed')
    expected_num = request.args.get('expected_num')
    genre = request.args.get('genre')
    piano = request.args.get('piano')
    guitar = request.args.get('guitar')
    drums = request.args.get('drums')
    bass = request.args.get('bass')
    vocals = request.args.get('vocals')
    violin = request.args.get('violin')
    viola = request.args.get('viola')
    cello = request.args.get('cello')

    # add code to add row to tickets and ticket_history tables
    # send an email to someone with information from form
    return jsonify(
        your_name=your_name,
        your_email=your_email,
        you=you,
        contact_name=contact_name,
        contact_email=contact_email,
        record_date1=record_date1,
        record_date2=record_date2,
        record_date3=record_date3,
        hours_needed=hours_needed,
        expected_num=expected_num,
        genre=genre,
        piano=piano,
        guitar=guitar,
        drums=drums,
        bass=bass,
        vocals=vocals,
        violin=violin,
        viola=viola,
        cello=cello
        )


@APP.route('/api/newticket')
def newticket_api():
    session_date = request.args.get('session_date')
    engineer_name = request.args.get('engineer_name')
    engineer_email = request.args.get('engineer_email')
    creator_name = request.args.get('creator_name')
    creator_email = request.args.get('creator_email')
    assignee_name = request.args.get('assignee_name')
    assignee_email = request.args.get('assignee_email')
    mixer_name = request.args.get('mixer_name')
    mixer_email = request.args.get('mixer_email')
    mixed_date = request.args.get('mixed_date')
    location_mixed = request.args.get('location_mixed')
    location_exported = request.args.get('location_exported')
    comments = request.args.get('comments')
    num_multitracks = request.args.get('num')

    # code to add row to tickets and ticket_history tables in database

    return jsonify(
        session_date=session_date,
        engineer_name=engineer_name,
        engineer_email=engineer_email,
        creator_name=creator_name,
        creator_email=creator_email,
        assignee_name=assignee_name,
        assignee_email=assignee_email,
        mixer_name=mixer_name,
        mixer_email=mixer_email,
        mixed_date=mixed_date,
        location_mixed=location_mixed,
        location_exported=location_exported,
        comments=comments,
        num_multitracks=num_multitracks
        )


@APP.route('/api/newmultitrack')
def newmultitrack_api():
    multitrack_name = request.args.get('multitrack_name')
    multitrack_id = request.args.get('multitrack_id')
    artist_name = request.args.get('artist_name')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    # code to add row to multitracks and multitrack_history tables in database

    return jsonify(
        multitrack_name=multitrack_name,
        multitrack_id=multitrack_id,
        artist_name=artist_name,
        start_time=start_time,
        end_time=end_time,
        

if __name__ == '__main__':
    APP.run(port=5080, host='0.0.0.0', debug='--debug' in sys.argv)




