"""
Main webapp.py function
"""
#!/usr/bin/env python
import os
import sqlite3
import time
import argparse
import numpy
from flask import Flask, jsonify, render_template, request, flash, redirect, url_for, send_from_directory
from flask_mail import Message, Mail
from request_record_email import BODY as request_record_body

APP = Flask(__name__)
APP.config.update(dict(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='medleydbaccess@gmail.com',
))

APP.config.update(dict(
    DATABASE=os.path.join(APP.root_path, 'static', 'ticketmanager.db'),
    UPLOAD_FOLDER="uploads"
))

def allowed_file(filename):
    allowed= '.' in filename and filename.rsplit('.', 1)[1] in ["pdf","jpg","jpeg","png"]
    return allowed


@APP.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
    # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if uploaded_file and allowed_file(uploaded_file.filename):
            uploaded_file.save(os.path.join(APP.config['UPLOAD_FOLDER'], uploaded_file.filename))
            return redirect(url_for('uploaded_file',filename=uploaded_file.filename))


@APP.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(APP.config['UPLOAD_FOLDER'], filename)


def send_mail(recipients, subject, body, attachment=None):
    print APP.config
    if not isinstance(recipients, list):
        recipients = [recipients]
    msg = Message(
        recipients=recipients,
        subject=subject,
        sender='medleydbaccess@gmail.com'
       )

    msg.body = body

    if attachment is not None:
        with APP.open_resource(attachment) as fp:
            msg.attach(attachment, "image/pdf", fp.read())
    MAIL.send(msg)

    return True


def connect_db():
    """
    Creates and connects to an sqlite3 database that will hold the
    data of tickets and multitracks.

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
    Formats headers of tables so underscores are replaced with spaces,
    and makes first letter of each word uppercase.

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

    tickets['url'] = []
    tickets['delete'] = []

    for row in cursor:
        for name, item in zip(tickets_headers, row):
            tickets[name].append(item)
        tickets['url'].append('/ticket?id={}'.format(row[0]))
        tickets['delete'].append('/api/deleteticket?ticket_number={}'.format(row[0]))

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

    multitracks_in_ticket['url'] = []
    multitracks_in_ticket['delete'] = []

    multitracks_cursor = rv.execute('select * from multitracks where ticket_number="{}"'.format(ticket_id))
    for row in multitracks_cursor:
        multitracks_in_ticket['url'].append('/multitrack?id={}'.format(row[2]))
        multitracks_in_ticket['delete'].append('/api/deletemultitrack?ticket_number={}'.format(row[2]))

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
    Views more information about a single multitrack within
     a ticket given a multitrack ID.
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

    multitrack_status = fill_table(multitrack_status_headers, multitrack_status_cursor)
    multitrack_history = fill_table(multitrack_history_headers, multitrack_history_cursor)

    return render_template('multitrack.html', multitrack_id=multitrack_id,
        db_multitrack_status_headers=multitrack_status_headers,
        formatted_multitrack_status_headers=formatted_multitrack_status_headers,
        db_multitrack_history_headers=multitrack_history_headers,
        formatted_multitrack_history_headers=formatted_multitrack_history_headers,
        multitrack_history=multitrack_history,
        multitrack_status=multitrack_status)


@APP.route('/newticket_multitracks')
def new_multitrack():
    """
    Renders page to fill out multitrack information

    Return
    ------
    newticket_multitracks.html: rendered page
    multitrack_number: int
    total_multitracks: int
    """
    multitrack_number = request.args.get('multitrack_number')
    total_multitracks = request.args.get('total_multitracks')
    return render_template('newticket_multitracks.html', 
        multitrack_number=multitrack_number, 
        total_multitracks=total_multitracks)

@APP.route('/thankyou')
def thankyou():
    """
    Renders thankyou.html page after new ticket request is finished.

    Return
    ------
    thankyou.html: rendered page
    """
    return render_template('thankyou.html')


@APP.route('/api/requestrecord')
def requestrecord_api():
    """
    API for requestrecord.html.
    """

    date_opened = time.strftime("%x")
    date_updated = time.strftime("%x")
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

    # add code to add row to tickets and ticket_history tables
    rv = connect_db()

    ticket_number_cursor = rv.execute("select ticket_number from tickets")
    ticket_numbers = [int(t[0]) for t in ticket_number_cursor]
    ticket_number = numpy.max(ticket_numbers) + 1

    rv.execute('insert into tickets values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
        ticket_number, "Requested", None, date_opened, date_updated, None, None, None, 
        your_name, your_email, "Julia Caruso", "julia.caruso@nyu.edu", genre, expected_num, None))

    rv.execute('insert into ticket_history values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
        ticket_number, "Requested", None, date_opened, date_updated, None, None, None, 
        your_name, your_email, "Julia Caruso", "julia.caruso@nyu.edu", genre, expected_num, None))

    rv.commit()


    # code to send automated email
    send_mail(
        "hmyip1@gmail.com", 
        # your_email
        "Confirming your Recording Session Request | MedleyDB Manager",
        "Thank you for submitting your request for a recording session in Dolan. We will contact you shortly about your recording session time and date.",
        attachment=None)

    send_mail(
        "hmyip1@gmail.com",
        #julia.caruso@nyu.edu
        "Request to Record | MedleyDB Manger",
        request_record_body.format(your_name, your_email, contact_name, contact_email, record_date1, record_date2, record_date3, hours_needed, expected_num),
        attachment=None)

    send_mail(
        "hmyip1@gmail.com",
        # MedleyD.taea5mqvehv6g5ij@u.box.com
        "Create Commons Consent Form | MedleyDB Manager",
        " ",
        attachment="consentform")

    return jsonify(
        date_opened=date_opened,
        date_updated=date_updated,
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
        genre=genre
        )


@APP.route('/api/newticket')
def newticket_api():
    """
    API for newticket.html
    """
    date_opened = time.strftime("%x")
    date_updated = time.strftime("%x")
    ticket_name = request.args.get('ticket_name')
    status = request.args.get('status')
    your_name = request.args.get('your_name')
    your_email = request.args.get('your_email')
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
    genre = request.args.get('genre')
    comments = request.args.get('comments')
    num_multitracks = request.args.get('num_multitracks')

    # code to add row to tickets and ticket_history tables in database
    rv = connect_db()

    ticket_number_cursor = rv.execute("select ticket_number from tickets")
    ticket_numbers = [int(t[0]) for t in ticket_number_cursor]
    ticket_number = numpy.max(ticket_numbers) + 1

    query='insert into tickets values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
        ticket_number, status, ticket_name, date_opened, date_updated, session_date,
        engineer_name, engineer_email, your_name, your_email,
        assignee_name, assignee_email, genre, num_multitracks, comments)
    rv.execute(query)

    rv.execute('insert into ticket_history values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
        ticket_number, status, ticket_name, 
        date_opened, date_updated, session_date, engineer_name,
        engineer_email, creator_name, creator_email, assignee_name,
        assignee_email, genre, num_multitracks, comments))

    rv.commit()


    return jsonify(
        date_opened=date_opened,
        date_updated=date_updated,
        ticket_name=ticket_name,
        status=status,
        your_name=your_name,
        your_email=your_email,
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
        genre=genre,
        comments=comments,
        num_multitracks=num_multitracks
        )

@APP.route('/api/deleteticket')
def deleteticket_api():
    ticket_number = request.args.get('ticket_number')
    rv = connect_db()

    rv.execute('delete from tickets where ticket_number={}'.format(ticket_number))
    rv.execute('delete from ticket_history where ticket_number={}'.format(ticket_number))
    rv.execute('delete from multitracks where ticket_number={}'.format(ticket_number))
    rv.execute('delete from multitrack_history where ticket_number={}'.format(ticket_number))
    rv.commit()

    return redirect(url_for("view_tickets"))

@APP.route('/api/updateticket')
def updateticket_api():

    status = request.args.get('status')
    session_date = request.args.get('session_date')
    engineer_name = request.args.get('engineer_name')
    engineer_email = request.args.get('engineer_email')
    assignee_name = request.args.get('assignee_name')
    assignee_email = request.args.get('assignee_email')
    comments = request.args.get('comments')

    # code to UPDATE row
    ticket_number = request.args.get('ticket_number')
    rv = connect_db()

    if status is not None:
        print status
        print ticket_number
        rv.execute('update tickets set status = "{}" where ticket_number = {}'.format(status, ticket_number))
        rv.execute('update ticket_history set status = "{}" where ticket_number = {}'.format(status, ticket_number))
        rv.execute('update multitracks set status = "{}" where ticket_number = {}'.format(status, ticket_number))
        rv.execute('update multitrack_history set status = "{}" where ticket_number = {}'.format(status, ticket_number))

    if session_date is not None:
        rv.execute('update tickets set session_date = "{}" where ticket_number = {}'.format(session_date, ticket_number))
        rv.execute('update ticket_history set session_date = "{}" where ticket_number = {}'.format(session_date, ticket_number))

    if engineer_name is not None:
        rv.execute('update tickets set engineer_name = "{}" where ticket_number = {}'.format(engineer_name, ticket_number))
        rv.execute('update ticket_history set engineer_name = "{}" where ticket_number = {}'.format(engineer_name, ticket_number))
        rv.execute('update multitracks set engineer_name = "{}" where ticket_number = {}'.format(engineer_name, ticket_number))
        rv.execute('update multitrack_history set engineer_name = "{}" where ticket_number = {}'.format(engineer_name, ticket_number))
    if engineer_email is not None:
        rv.execute('update tickets set engineer_email = "{}" where ticket_number = {}'.format(engineer_email, ticket_number))
        rv.execute('update ticket_history set engineer_email = "{}" where ticket_number = {}'.format(engineer_email, ticket_number))
        rv.execute('update multitracks set engineer_email = "{}" where ticket_number = {}'.format(engineer_email, ticket_number))
        rv.execute('update multitrack_history set engineer_email = "{}" where ticket_number = {}'.format(engineer_email, ticket_number))
    if assignee_name is not None:
        rv.execute('update tickets set assignee_name = "{}" where ticket_number = {}'.format(assignee_name, ticket_number))
        rv.execute('update ticket_history set assignee_name = "{}" where ticket_number = {}'.format(assignee_name, ticket_number))
        
    if assignee_email is not None:
        rv.execute('update tickets set assignee_email = "{}" where ticket_number = {}'.format(assignee_email, ticket_number))
        rv.execute('update ticket_history set assignee_email = "{}" where ticket_number = {}'.format(assignee_email, ticket_number))
        
    if comments is not None:
        rv.execute('update tickets set comments = "{}" where ticket_number = {}'.format(comments, ticket_number))
        rv.execute('update ticket_history set comments = "{}" where ticket_number = {}'.format(comments, ticket_number))
        rv.execute('update multitracks set comments = "{}" where ticket_number = {}'.format(comments, ticket_number))
        rv.execute('update multitrack_history set comments = "{}" where ticket_number = {}'.format(comments, ticket_number))
    
    rv.commit()

 

    return jsonify(
        status=status,
        session_date=session_date,
        engineer_name=engineer_name,
        engineer_email=engineer_email,
        assignee_name=assignee_name,
        assignee_email=assignee_email,
        comments=comments
        )



@APP.route('/api/newmultitrack')
def newmultitrack_api():
    """
    API for newticket_multitrack.html
    """
    ticket_number = request.args.get('ticket_number')

    your_name = request.args.get('your_name')
    your_email = request.args.get('your_email')
    status = request.args.get('status')
    engineer_name = request.args.get('engineer_name')
    engineer_email = request.args.get('engineer_email')
    mixer_name = request.args.get('mixer_name')
    mixer_email = request.args.get('mixer_email')
    bouncer_name = request.args.get('bouncer_name')
    bouncer_email = request.args.get('bouncer_email')
    comments = request.args.get('comments')

    date_opened = time.strftime("%x")
    date_updated = time.strftime("%x")
    multitrack_name = request.args.get('multitrack_name')
    multitrack_id = request.args.get('multitrack_id')
    artist_name = request.args.get('artist_name')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    genre = request.args.get('genre')
    num_instruments = request.args.get('num_instruments')

    # code to add row to multitracks and multitrack_history tables in database
    rv.execute('insert into multitracks_in_ticket values("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format(
        ticket_number, status, multitrack_id, date_opened, date_updated, 
        artist_name, multitrack_name, genre, num_instruments,
        your_name, your_email, engineer_name, engineer_email, 
        mixer_name, mixer_email, bouncer_name, bouncer_email, comments))

    rv.execute('insert into multitrack_history values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
        ticket_number, status, multitrack_id,
        date_opened, date_updated, artist_name, multitrack_name, genre,
        num_instruments, your_name, your_email, engineer_name, engineer_email, 
        mixer_name, mixer_email, bouncer_name, bouncer_email, comments))

    rv.commit()

    return jsonify(
        ticket_number=ticket_number,
        your_name=your_name,
        your_email=your_email,
        status=status,
        engineer_name=engineer_name,
        engineer_email=engineer_email,
        mixer_name=mixer_name,
        mixer_email=mixer_email,
        bouncer_name=bouncer_name,
        bouncer_email=bouncer_email,
        comments=comments,
        date_opened=date_opened,
        date_updated=date_updated,
        multitrack_name=multitrack_name,
        multitrack_id=multitrack_id,
        artist_name=artist_name,
        start_time=start_time,
        end_time=end_time,
        genre=genre,
        num_instruments=num_instruments)


@APP.route('/api/deletemultitrack')
def deletemultitrack_api():
    ticket_number = request.args.get('ticket_number')
    rv = connect_db()

    rv.execute('delete from multitracks where ticket_number={}'.format(ticket_number))
    rv.execute('delete from multitrack_history where ticket_number={}'.format(ticket_number))
    rv.commit()

    return redirect(url_for("viewtickets"))






if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="medleydb_webapp"
        )
    parser.add_argument("password", type=str, help="medleydb gmail password")
    parser.add_argument("--debug", action="store_const", const=True, default=False)
    args = parser.parse_args()
    APP.config.update(dict(MAIL_PASSWORD = args.password))

    MAIL = Mail(APP)

    APP.run(port=5080, host='0.0.0.0', debug=args.debug)


