"""
Main webapp.py function
"""
#!/usr/bin/env python
import os
from time import gmtime, strftime
import argparse
import numpy
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_mail import Mail
from utils import connect_db, get_header, send_mail
from utils import fill_table, format_headers, format_comments, allowed_file
from emails import REQUEST_BODY as request_record_body
from emails import ASSIGNEE_BODY as assignee_body
from functools import wraps
import csv

AUTH_INFO = ".auth_info"
def load_auth_info():
    with open(AUTH_INFO) as fhandle:
        reader=csv.reader(fhandle, delimiter = ",")
        for line in reader:
            username, password = line
            break
    return username, password

USERNAME, PASSWORD = load_auth_info()

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

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == USERNAME and password == PASSWORD

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated



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


@APP.route('/api/requestrecord')
def requestrecord_api():
    """
    API for requestrecord.html.
    Inserts info retrieved from requestrecord.html form into tickets and ticket_history tables.
    Sends automated conformition emails.

    Returns
    -------
    str(ticket_number): string
    """

    date_opened = strftime("%m-%d-%y %H:%M:%S", gmtime())
    date_updated = strftime("%m-%d-%y %H:%M:%S", gmtime())
    your_name = request.args.get('your_name')
    your_email = request.args.get('your_email')
    record_date1 = request.args.get('record_date1')
    record_date2 = request.args.get('record_date2')
    record_date3 = request.args.get('record_date3')
    hours_needed = request.args.get('hours_needed')
    num_multitracks = request.args.get('num_multitracks')
    genre = request.args.get('genre')
    comments = request.args.get('comments')
    formatted_comments = format_comments(comments)

    # add code to add row to tickets and ticket_history tables
    db_connection = connect_db(APP)

    ticket_number_cursor = db_connection.execute("select ticket_number from tickets")
    ticket_numbers = [int(t[0]) for t in ticket_number_cursor]
    if len(ticket_numbers) == 0:
        ticket_number = 1
    else:
        ticket_number = numpy.max(ticket_numbers) + 1

    ticket_revision_id_cursor = db_connection.execute(
        "select ticket_revision_id from ticket_history where ticket_number={}".format(ticket_number))
    ticket_revision_ids_strings = [t[0].split("-")[1] for t in ticket_revision_id_cursor]
    ticket_revision_ids = [int(t) for t in ticket_revision_ids_strings]
    if len(ticket_revision_ids_strings) == 0:
        ticket_revision_id = "{}-1".format(ticket_number)
    else:
        ticket_revision_number = numpy.max(ticket_revision_ids) + 1
        ticket_revision_id = "{}-{}".format(ticket_number, ticket_revision_number)

    db_connection.execute(
        'insert into tickets values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
            ticket_number, "Requested", None, date_opened, date_updated, "0", genre, "TBD",
            your_name, your_email, "TBD", "TBD", "Julia Caruso", 
            "julia.caruso@nyu.edu", "TBD", "TBD", "TBD", "TBD", formatted_comments)
    )

    db_connection.execute(
        'insert into ticket_history values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
            ticket_number, ticket_revision_id, "Requested", None, date_opened, date_updated, "0", genre, "TBD",
            your_name, your_email, "TBD", "TBD",  "Julia Caruso",
            "julia.caruso@nyu.edu", "TBD","TBD","TBD","TBD", formatted_comments)
    )
    db_connection.commit()


    # code to send automated email
    send_mail(
        APP, MAIL,
        "hmyip1@gmail.com",
        # your_email
        "Confirming your Recording Session Request | MedleyDB Manager",
        "Thank you for submitting your request for a recording session in Dolan. We will contact you shortly about your recording session time and date.",
        attachment=None
    )

    send_mail(
        APP, MAIL,
        "hmyip1@gmail.com",
        #julia.caruso@nyu.edu
        "Request to Record | MedleyDB Manger",
        request_record_body.format(
            your_name, your_email, record_date1,
            record_date2, record_date3, hours_needed, num_multitracks, comments
        ),
        attachment=None
    )

    return str(ticket_number)

@APP.route('/newticket')
def new_ticket():
    """
    Renders newticket.html template

    Returns
    -------
    'newticket.html': template
    """
    return render_template('newticket.html', var1=None, var2=None)

@APP.route('/newticket_multitracks')
def new_multitrack():
    """
    Renders page to fill out multitrack information

    Return
    ------
    newticket_multitracks.html: rendered page
    multitrack_number: int
    num_multitracks: int
    """
    multitrack_number = request.args.get('multitrack_number')
    num_multitracks = request.args.get('num_multitracks')

    return render_template(
        'newticket_multitracks.html',
        multitrack_number=multitrack_number,
        num_multitracks=num_multitracks
    )

@APP.route('/api/newmultitrack')
def newmultitrack_api():
    """
    API for newticket_multitrack.html
    Adds 1 to num_multitracks, adds a multitrack to the multitracks table, changes date updated

    Returns
    -------
    ticket_number: string
    num_multitracks: string 
    multitrack_id: string
    ticket_revision_id: string
    date_updated: string
    """
    
    db_connection = connect_db(APP)
    temp = request.args.get('update_ticket_history')
    if temp == "true":
        update_ticket_history = True
    elif temp == "false":
        update_ticket_history = False
    ticket_number = request.args.get('ticket_number')
    date_updated = strftime("%m-%d-%y %H:%M:%S", gmtime())

    multitrack_id_cursor = db_connection.execute(
        "select multitrack_id from multitracks where ticket_number={}".format(ticket_number)
    )
    multitrack_ids_strings = [t[0].split("-")[1] for t in multitrack_id_cursor]
    multitrack_ids = [int(t) for t in multitrack_ids_strings]

    if len(multitrack_ids_strings) == 0:
        multitrack_id = "{}-1".format(ticket_number)
    else:    
        multitrack_number = multitrack_ids.pop() + 1
        multitrack_id = "{}-{}".format(ticket_number, multitrack_number)

    ticket_revision_id_cursor = db_connection.execute(
    "select ticket_revision_id from ticket_history where ticket_number={}".format(ticket_number)
    )
    ticket_revision_ids_strings = [t[0].split("-")[1] for t in ticket_revision_id_cursor]
    ticket_revision_ids = [int(t) for t in ticket_revision_ids_strings]

    if len(ticket_revision_ids_strings) == 0: 
        ticket_revision_id = "{}-1".format(ticket_number)
    else:    
        ticket_revision_number = numpy.max(ticket_revision_ids) + 1
        ticket_revision_id = "{}-{}".format(ticket_number, ticket_revision_number)

    date_opened = strftime("%m-%d-%y %H:%M:%S", gmtime())
    title = request.args.get('title')
    artist_name = request.args.get('artist_name')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    genre = request.args.get('genre')
    num_instruments = request.args.get('num_instruments')


    # code to add row to multitracks
    db_connection.execute(
        'insert into multitracks values("{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format(
            ticket_number, multitrack_id, date_opened, title,
            artist_name,  genre, start_time, end_time, num_instruments)
    )

    num_multitracks_cursor = db_connection.execute(
        "select * from multitracks where ticket_number={}".format(ticket_number))
    num_multitracks_list = [t[0] for t in num_multitracks_cursor]
    num_multitracks = len(num_multitracks_list)


    ticket_history_cursor = db_connection.execute('select * from ticket_history where ticket_number={} order by date_updated'.format(ticket_number))
    rows = [list(t) for t in ticket_history_cursor]
    row = rows[-1]

    row[1] = ticket_revision_id
    if date_updated != "":
        row[5] = date_updated
        db_connection.execute('update tickets set date_updated = "{}" where ticket_number = {}'.format(date_updated, ticket_number))

    if num_multitracks != "":
        row[6] = str(num_multitracks)
        db_connection.execute('update tickets set number_of_tracks = "{}" where ticket_number = {}'.format(str(num_multitracks), ticket_number))

    row = [str(r) if r != "" else u"" for r in row]

    insert_vals = '","'.join(row)

    if update_ticket_history == True:
        db_connection.execute(
            'insert into ticket_history values("{}");'.format(insert_vals)
            )

    db_connection.commit()

    return jsonify(ticket_number=ticket_number, 
        num_multitracks=num_multitracks, 
        multitrack_id=multitrack_id, 
        ticket_revision_id=ticket_revision_id, 
        date_updated=date_updated)
   


@APP.route('/viewtickets')
@requires_auth
def view_tickets():
    """
    Renders viewtickets.html template

    Returns
    -------
    'viewtickets.html': renders to a template
    tickets: dictionary
        empty entrys in the tickets table
    tickets_headers: list
        headers from the tickets table
    formatted_tickets_headers: list
        formatted headers from tickets table
    """
    db_connection = connect_db(APP)
    cursor = db_connection.execute('select * from tickets')

    tickets_headers = get_header(APP, 'tickets')
    formatted_tickets_headers = [format_headers(h) for h in tickets_headers]

    tickets = {}
    for name in tickets_headers:
        tickets[name] = []

    tickets['url'] = []
    tickets['delete'] = []

    for row in cursor:
        if row[1]=="Complete":
            continue
        for name, item in zip(tickets_headers, row):
            tickets[name].append(item)
        tickets['url'].append('/ticket?ticket_number={}'.format(row[0]))
        tickets['delete'].append(
            '/api/deleteticket?ticket_number={}'.format(row[0])
        )


    return render_template(
        'viewtickets.html', tickets=tickets,
        tickets_headers=tickets_headers,
        formatted_tickets_headers=formatted_tickets_headers
    )



@APP.route('/completedtickets')
def completed_tickets():
    db_connection = connect_db(APP)
    completed_tickets_cursor = db_connection.execute(
        'select * from tickets where status="Complete"')

    print completed_tickets_cursor

    completed_tickets_headers = get_header(APP, 'tickets')
    formatted_completed_tickets_headers = [
        format_headers(h) for h in completed_tickets_headers]

    completed_tickets = {}
    for name in completed_tickets_headers:
        completed_tickets[name] = []

    completed_tickets['url'] = []
    completed_tickets['delete'] = []

    for row in completed_tickets_cursor:
        for name, item in zip(completed_tickets_headers, row):
            completed_tickets[name].append(item)
        completed_tickets['url'].append('/ticket?ticket_number={}'.format(row[0]))
        completed_tickets['delete'].append(
            '/api/deleteticket?ticket_number={}'.format(row[0])
        )

    
    return render_template(
        'completedtickets.html',
        tickets=completed_tickets,
        completed_tickets=completed_tickets,
        completed_tickets_headers=completed_tickets_headers,
        formatted_completed_tickets_headers=formatted_completed_tickets_headers
    )


@APP.route('/ticket')
def ticket():
    """
    Views more information about a single ticket given a ticket ID.
    Gives info on status of ticket, its history, and multitracks in the ticket.

    Return
    ------
    'ticket.html': rendered template
    ticket_number: int
        requested by the user
    ticket_status_headers: list
        headers of ticket status table
    formatted_ticket_status_headers: list
        formatted headers of ticket status table
    ticket_history_headers: list
        headers of ticket history table
    formatted_ticket_history_headers: list
        formatted headers of ticket history table
    multitracks_headers: list
        headers of multitracks in ticket table
    formatted_multitracks_headers: list
        formatted headers of multitracks in ticket tabls
    tickets: dictionary
        content in tickets table
    ticket_history: dictionary
        contents in ticket history table
    multitracks: dictionary
        contents in multitracks in ticket table
    update_ticket_url: string url
    add_multitrack_url: string url


    """
    db_connection = connect_db(APP)

    ticket_number = request.args.get('ticket_number')
    ticket_name = request.args.get('ticket_name')
    num_multitracks = request.args.get('num_multitracks')
    multitrack_id = request.args.get('multitrack_id')
    
    ticket_status_headers = get_header(APP, 'tickets')
    ticket_history_headers = get_header(APP, 'ticket_history')
    multitracks_headers = get_header(APP, 'multitracks')

    formatted_ticket_status_headers = [
        format_headers(h) for h in ticket_status_headers
    ]
    formatted_ticket_history_headers = [
        format_headers(h) for h in ticket_history_headers
    ]
    formatted_multitracks_headers = [
        format_headers(h) for h in multitracks_headers
    ]

    ticket_status_cursor = db_connection.execute(
        'select * from tickets where ticket_number="{}"'.format(ticket_number)
    )
    ticket_history_cursor = db_connection.execute(
        'select * from ticket_history where ticket_number="{}"'.format(ticket_number)
    )
    multitracks_cursor = db_connection.execute(
        'select * from multitracks where ticket_number="{}"'.format(ticket_number)
    )

    tickets = fill_table(ticket_status_headers, ticket_status_cursor)
    ticket_history = fill_table(ticket_history_headers, ticket_history_cursor)
    multitracks = fill_table(multitracks_headers, multitracks_cursor)
    
    multitracks['url'] = []
    multitracks_cursor = db_connection.execute(
        'select * from multitracks where ticket_number="{}"'.format(ticket_number)
    )

    multitracks['delete'] = []
    update_ticket_url = "/ticket_update?ticket_number={}".format(ticket_number)
    add_multitrack_url = "/ticket_addMultitrack?ticket_number={}&num_multitracks={}".format(ticket_number, num_multitracks)

    for row in multitracks_cursor:
        multitracks['url'].append('/multitrack?multitrack_id={}&ticket_number={}'.format(row[1], ticket_number))
        multitracks['delete'].append(
            '/api/deletemultitrack?multitrack_id={}&ticket_number={}'.format(row[1], ticket_number))

    return render_template(
        'ticket.html', ticket_number=ticket_number,
        ticket_name=ticket_name,
        multitrack_id=multitrack_id, 
        num_multitracks=num_multitracks,
        ticket_status_headers=ticket_status_headers,
        formatted_ticket_status_headers=formatted_ticket_status_headers,
        ticket_history_headers=ticket_history_headers,
        formatted_ticket_history_headers=formatted_ticket_history_headers,
        multitracks_headers=multitracks_headers,
        formatted_multitracks_headers=formatted_multitracks_headers,
        tickets=tickets,
        ticket_history=ticket_history,
        multitracks=multitracks,
        update_ticket_url=update_ticket_url,
        add_multitrack_url=add_multitrack_url

    )


@APP.route('/api/deleteticket')
def deleteticket_api():
    """
    Deletes a ticket from the tickets table.

    Returns
    -------
    Refreshes viewtickets.html
    """

    ticket_number = request.args.get('ticket_number')
    db_connection = connect_db(APP)

    db_connection.execute('delete from tickets where ticket_number={}'.format(ticket_number))
    db_connection.execute('delete from ticket_history where ticket_number={}'.format(ticket_number))
    db_connection.execute('delete from multitracks where ticket_number={}'.format(ticket_number))
    db_connection.commit()

    return redirect(url_for("view_tickets"))


@APP.route('/ticket_update')
def ticket_update():
    """
    Renders ticket_update.html template

    Returns
    -------
    'tickat_update.html': template
    """
    ticket_number = request.args.get('ticket_number')
    ticket_revision_id = request.args.get('ticket_revision_id')

    return render_template('ticket_update.html',
        ticket_number=ticket_number,
        ticket_revision_id=ticket_revision_id)


@APP.route('/api/updateticket')
def updateticket_api():

    """
    API for updating ticket
    Updates value in tickets table, add entry to ticket_history

    Returns
    -------
    ticket_number: string
    status: string
    ticket_name: string
    date_updated: string
    session_date: string
    engineer_name: string
    engineer_email: string
    assignee_name: string
    assignee_email: string
    mixer_name: string
    mixer_email: string
    bouncer_name: string
    bouncer_email: string
    comments: string
    """

    status = request.args.get('status')
    ticket_name = request.args.get('ticket_name')
    genre = request.args.get('genre')
    date_updated = strftime("%m-%d-%y %H:%M:%S", gmtime())
    session_date = request.args.get('session_date')
    your_name = request.args.get('your_name')
    your_email = request.args.get('your_email')
    engineer_name = request.args.get('engineer_name')
    engineer_email = request.args.get('engineer_email')
    assignee_name = request.args.get('assignee_name')
    assignee_email = request.args.get('assignee_email')
    mixer_name = request.args.get('mixer_name')
    mixer_email = request.args.get('mixer_email')
    bouncer_name = request.args.get('bouncer_name')
    bouncer_email = request.args.get('bouncer_email')
    comments = request.args.get('comments')
    formatted_comments = format_comments(comments)
    mixed_date = request.args.get('mixed_date')
    location_mixed = request.args.get('location_mixed')
    location_exported = request.args.get('location_exported')

    db_connection = connect_db(APP)
    # code to UPDATE row
    ticket_number = request.args.get('ticket_number')

    ticket_revision_id_cursor = db_connection.execute(
    "select ticket_revision_id from ticket_history where ticket_number={}".format(ticket_number)
    )
    ticket_revision_ids_strings = [t[0].split("-")[1] for t in ticket_revision_id_cursor]
    ticket_revision_ids = [int(t) for t in ticket_revision_ids_strings]
    if len(ticket_revision_ids_strings) == 0:
        ticket_revision_id = "{}-1".format(ticket_number)
    else:
        ticket_revision_number = numpy.max(ticket_revision_ids) + 1
        ticket_revision_id = "{}-{}".format(ticket_number, ticket_revision_number)


    ticket_history_cursor = db_connection.execute('select * from ticket_history where ticket_number={} order by date_updated'.format(ticket_number))
    rows = [list(t) for t in ticket_history_cursor]
    row = rows[-1]

    row[1] = ticket_revision_id
    
    if status != "null":
        row[2] = status
        db_connection.execute('update tickets set status = "{}" where ticket_number = {}'.format(status, ticket_number))
    if ticket_name != "":
        row[3] = ticket_name
        db_connection.execute('update tickets set ticket_name = "{}" where ticket_number = {}'.format(ticket_name, ticket_number))
    if genre != "null":
        row[6] = genre
        db_connection.execute('update tickets set genre = "{}" where ticket_number  = "{}"'.format(genre, ticket_number))
    if date_updated != "":
        row[5] = date_updated
        db_connection.execute('update tickets set date_updated = "{}" where ticket_number = {}'.format(date_updated, ticket_number))
    if session_date!= "":
        row[8] = session_date
        db_connection.execute('update tickets set session_date = "{}" where ticket_number = {}'.format(session_date, ticket_number))
    if your_name != "":
        row[9] = your_name
        db_connection.execute('update tickets set creator_name = "{}" where ticket_number = {}'.format(your_name, ticket_number))
    if your_email != "":
        row[10] = your_email
        db_connection.execute('update tickets set creator_email = "{}" where ticket_number = {}'.format(your_email, ticket_number))
    if engineer_name != "":
        row[11] = engineer_name
        db_connection.execute('update tickets set engineer_name = "{}" where ticket_number = {}'.format(engineer_name, ticket_number))
    if engineer_email != "":
        row[12] = engineer_email
        db_connection.execute('update tickets set engineer_email = "{}" where ticket_number = {}'.format(engineer_email, ticket_number))
    if assignee_name != "":
        row[13] = assignee_name
        db_connection.execute('update tickets set assignee_name = "{}" where ticket_number = {}'.format(assignee_name, ticket_number))
    if assignee_email != "":
        row[14] = assignee_email
        db_connection.execute('update tickets set assignee_email = "{}" where ticket_number = {}'.format(assignee_email, ticket_number))
        send_mail(
            APP, MAIL,
            [assignee_email, "rachel.bittner@nyu.edu"],
            "You are the new Assignee of a Ticket | MedleyDB Manager",
            assignee_body.format(mixed_date, location_mixed, location_exported, ticket_number),
            attachment=None
        )
    if mixer_name != "":
        row[15] = mixer_name
        db_connection.execute('update tickets set mixer_name = "{}" where ticket_number = {}'.format(mixer_name, ticket_number))
    if mixer_email != "":
        row[16] = mixer_email
        db_connection.execute('update tickets set mixer_email = "{}" where ticket_number = {}'.format(mixer_email, ticket_number))
    if bouncer_name != "":
        row[17] = bouncer_name
        db_connection.execute('update tickets set bouncer_name = "{}" where ticket_number = {}'.format(bouncer_name, ticket_number))
    if bouncer_email != "":
        row[18] = bouncer_email
        db_connection.execute('update tickets set bouncer_email = "{}" where ticket_number = {}'.format(bouncer_email, ticket_number))
    if comments != "":
        row[19] = formatted_comments
        db_connection.execute('update tickets set comments = "{}" where ticket_number = {}'.format(formatted_comments, ticket_number))

    row = [str(r) if r != "" else u"" for r in row]
    insert_vals = '","'.join(row)

    db_connection.execute(
            'insert into ticket_history values("{}");'.format(insert_vals)
            )
    
    db_connection.commit()


    return jsonify(
        ticket_number=ticket_number,
        status=status,
        ticket_name=ticket_name,
        date_updated=date_updated,
        genre=genre,
        session_date=session_date,
        your_name=your_name,
        your_email=your_email,
        engineer_name=engineer_name,
        engineer_email=engineer_email,
        assignee_name=assignee_name,
        assignee_email=assignee_email,
        mixer_name=mixer_name,
        mixer_email=mixer_email,
        bouncer_name=bouncer_name,
        bouncer_email=bouncer_email,
        mixed_date=mixed_date,
        location_mixed=location_mixed,
        location_exported=location_exported,
        comments=comments,
        formatted_comments=formatted_comments
        )


@APP.route('/ticket_addMultitrack')
def ticket_addMultitrack():
    """
    Renders tickets_addMultitrack.html template

    Returns
    -------
    'ticket_addMultitrack.html': template
    ticket_number: string
    num_multitracks: string
    ticket_revision_id: string
    date_updated: string

    """
    ticket_number = request.args.get("ticket_number")
    num_multitracks = request.args.get("num_multitracks")
    ticket_revision_id = request.args.get("ticket_revision_id")
    date_updated = strftime("%m-%d-%y %H:%M:%S", gmtime())

    return render_template('ticket_addMultitrack.html', 
        ticket_number=ticket_number, 
        num_multitracks=num_multitracks, 
        ticket_revision_id=ticket_revision_id, 
        date_updated=date_updated)


@APP.route('/multitrack')
def multitrack():
    """
    Views more information about a single multitrack within a ticket given a multitrack ID.
    Gives info on status of multitrack.

    Return
    ------
    'multitrack.html': rendered template
    multitrack_id: int
        requested by the user
    ticket_status_headers: list
        headers of ticket status table
    formatted_ticket_status_headers: list
        formatted headers of ticket status table
    multitrack_status: dictionary
        contents in multitrack status table

    """
    ticket_number = request.args.get('ticket_number')
    multitrack_id = request.args.get('multitrack_id')
    db_connection = connect_db(APP)

    multitrack_status_headers = get_header(APP, 'multitracks')
    formatted_multitrack_status_headers = [
        format_headers(h) for h in multitrack_status_headers
    ]

    multitrack_status_cursor = db_connection.execute(
        'select * from multitracks where multitrack_id="{}"'.format(
            multitrack_id
        )
    )

    multitrack_status = fill_table(
        multitrack_status_headers, multitrack_status_cursor
    )

    update_multitrack_url = "/multitrack_update?multitrack_id={}&ticket_number={}".format(str(multitrack_id),ticket_number)
    ticket_url = "/ticket?ticket_number={}".format(ticket_number)
    return render_template(
        'multitrack.html', multitrack_id=multitrack_id,
        ticket_number=ticket_number,
        multitrack_status_headers=multitrack_status_headers,
        formatted_multitrack_status_headers=formatted_multitrack_status_headers,
        multitrack_status=multitrack_status,
        update_multitrack_url=update_multitrack_url,
        ticket_url=ticket_url
    )


@APP.route('/api/deletemultitrack')
def deletemultitrack_api():
    """
    Deletes a multitrack from the multitracks, adds entry to ticket_history

    Returns
    -------
    Redirects page to ticket info
    """

    db_connection = connect_db(APP)
    date_updated = strftime("%m-%d-%y %H:%M:%S", gmtime())
    ticket_number = request.args.get('ticket_number')
    multitrack_id = request.args.get('multitrack_id')
    
    ticket_revision_id_cursor = db_connection.execute(
    "select ticket_revision_id from ticket_history where ticket_number={}".format(ticket_number))
    ticket_revision_ids_strings = [t[0].split("-")[1] for t in ticket_revision_id_cursor]
    ticket_revision_ids = [int(t) for t in ticket_revision_ids_strings]
    if len(ticket_revision_ids_strings) == 0:
        ticket_revision_id = "{}-1".format(ticket_number)
    else:    
        ticket_revision_number = numpy.max(ticket_revision_ids) + 1
        ticket_revision_id = "{}-{}".format(ticket_number, ticket_revision_number)

    temp_cursor = db_connection.execute('select * from tickets where ticket_number={} order by date_updated asc'.format(ticket_number))
    temp_row = list(temp_cursor.next())

    ticket_history_cursor = db_connection.execute('select * from ticket_history where ticket_number={} order by date_updated'.format(ticket_number))
    rows = [list(t) for t in ticket_history_cursor]
    row = rows[-1]

    db_connection.execute(
             'delete from multitracks where multitrack_id="{}"'.format(multitrack_id))

    num_multitracks_cursor = db_connection.execute(
        "select * from multitracks where ticket_number={}".format(ticket_number))
    num_multitracks_list = [t[0] for t in num_multitracks_cursor]
    num_multitracks = str(len(num_multitracks_list))

    row[1] = ticket_revision_id

    if date_updated != "":
        row[5] = date_updated
        db_connection.execute('update tickets set date_updated = "{}" where ticket_number = {}'.format(date_updated, ticket_number))

    if num_multitracks != "":
        row[6] = str(num_multitracks)
        db_connection.execute('update tickets set number_of_tracks = {} where ticket_number = {}'.format(num_multitracks, ticket_number))

    row = [str(r) if r != "" else u"" for r in row]
    
    insert_vals = '","'.join(row)
    db_connection.execute(
        'insert into ticket_history values("{}");'.format(insert_vals)
        )

    db_connection.commit()

    return redirect("/ticket?ticket_number={}".format(ticket_number))


@APP.route('/multitrack_update')
def multitrack_update():
    """
    Renders multitrack_update.html template

    Returns
    -------
    'multitrack_update.html': template
    """
    ticket_number = request.args.get('ticket_number')
    multitrack_id = request.args.get('multitrack_id')
    return render_template('multitrack_update.html', ticket_number=ticket_number, multitrack_id=multitrack_id)


@APP.route('/api/updatemultitrack')
def updatemultitrack_api():

    """
    API for updating multitrack
    Updates value in multitracks table

    Returns
    -------
   
    """

    title = request.args.get('title')
    artist_name = request.args.get('artist_name')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    genre = request.args.get('genre')
    num_instruments = request.args.get('num_instruments')

    db_connection = connect_db(APP)
    # code to UPDATE row
    ticket_number = request.args.get('ticket_number')
    multitrack_id = request.args.get('multitrack_id')

    if title != "":
        db_connection.execute('update multitracks set title = "{}" where multitrack_id  = "{}"'.format(title, multitrack_id))
    if artist_name != "":
        db_connection.execute('update multitracks set artist = "{}" where multitrack_id  = "{}"'.format(artist_name, multitrack_id))
    if start_time != "":
        db_connection.execute('update multitracks set start_time = "{}" where multitrack_id  = "{}"'.format(start_time, multitrack_id))
    if end_time != "":
        db_connection.execute('update multitracks set end_time = "{}" where multitrack_id  = "{}"'.format(end_time, multitrack_id))
    if genre != "null":
        db_connection.execute('update multitracks set genre = "{}" where multitrack_id  = "{}"'.format(genre, multitrack_id))
    if num_instruments != "":
        db_connection.execute('update multitracks set number_of_instruments = "{}" where multitrack_id  = "{}"'.format(num_instruments, multitrack_id))
    
    db_connection.commit()

    return jsonify(
        multitrack_id=multitrack_id,
        ticket_number=ticket_number,
        title=title,
        artist_name=artist_name,
        start_time=start_time,
        end_time=end_time,
        genre=genre,
        num_instruments=num_instruments
        )


@APP.route('/thankyou')
def thankyou():
    """
    Renders thankyou.html page after new ticket request is finished.

    Return
    ------
    thankyou.html: rendered page
    """
    return render_template('thankyou.html')


@APP.route('/instructions')
def instructions():
    """
    Renders instructions.html template

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


@APP.route('/api/newticket')
def newticket_api():
    """
    API for newticket.html
    Inserts info retrieved from newticket.html into tickets and ticket_history tables.

    Returns
    -------
    All variables passed.

    """
    date_opened = strftime("%m-%d-%y %H:%M:%S", gmtime())
    date_updated = strftime("%m-%d-%y %H:%M:%S", gmtime())
    ticket_name = request.args.get('ticket_name')
    status = request.args.get('status')
    your_name = request.args.get('your_name')
    your_email = request.args.get('your_email')
    session_date = request.args.get('session_date')
    engineer_name = request.args.get('engineer_name')
    engineer_email = request.args.get('engineer_email')
    assignee_name = request.args.get('assignee_name')
    assignee_email = request.args.get('assignee_email')
    mixer_name = request.args.get('mixer_name')
    mixer_email = request.args.get('mixer_email')
    bouncer_name = request.args.get('bouncer_name')
    bouncer_email = request.args.get('bouncer_email')
    mixed_date = request.args.get('mixed_date')
    location_mixed = request.args.get('location_mixed')
    location_exported = request.args.get('location_exported')
    genre = request.args.get('genre')
    comments = request.args.get('comments')
    formatted_comments = format_comments(comments)
    num_multitracks = request.args.get('num_multitracks')

    # code to add row to tickets and ticket_history tables in database
    db_connection = connect_db(APP)

    ticket_number_cursor = db_connection.execute(
        "select ticket_number from tickets"
    )
    ticket_numbers = [int(t[0]) for t in ticket_number_cursor]
    if len(ticket_numbers) == 0:
        ticket_number=1
    else:
        ticket_number = numpy.max(ticket_numbers) + 1

    ticket_revision_id_cursor = db_connection.execute(
    "select ticket_revision_id from ticket_history where ticket_number={}".format(ticket_number)
    )
    ticket_revision_ids_strings = [t[0].split("-")[1] for t in ticket_revision_id_cursor]
    ticket_revision_ids = [int(t) for t in ticket_revision_ids_strings]

    if len(ticket_revision_ids_strings) == 0:
        ticket_revision_id = "{}-1".format(ticket_number)
    else:    
        ticket_revision_number = numpy.max(ticket_revision_ids) + 1
        ticket_revision_id = "{}-{}".format(ticket_number, ticket_revision_number)

    db_connection.execute(
        'insert into tickets values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
            ticket_number, status, ticket_name, date_opened, date_updated, num_multitracks, genre, 
            session_date, your_name, your_email, engineer_name, engineer_email, 
            assignee_name, assignee_email, mixer_name, mixer_email, bouncer_name, bouncer_email, 
             formatted_comments)
    )

    db_connection.execute(
        'insert into ticket_history values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
            ticket_number, ticket_revision_id, status, ticket_name, date_opened, date_updated, num_multitracks, genre, 
            session_date, your_name, your_email, engineer_name, engineer_email, 
            assignee_name, assignee_email, mixer_name, mixer_email, bouncer_name, bouncer_email, 
             formatted_comments)
    )

    db_connection.commit()

    send_mail(
        APP, MAIL,
        "hmyip1@gmail.com",
        # your_email
        "Confirming a New Ticket | MedleyDB Manager",
        "Thank you for creating a new ticket in MedleyDB Manager. You can view your ticket on the table now.",
        attachment=None
    )

    return jsonify(
        ticket_number=ticket_number,
        ticket_revision_id=ticket_revision_id,
        date_opened=date_opened,
        date_updated=date_updated,
        ticket_name=ticket_name,
        status=status,
        your_name=your_name,
        your_email=your_email,
        session_date=session_date,
        engineer_name=engineer_name,
        engineer_email=engineer_email,
        assignee_name=assignee_name,
        assignee_email=assignee_email,
        mixer_name=mixer_name,
        mixer_email=mixer_email,
        bouncer_name=bouncer_name,
        bouncer_email=bouncer_email,
        mixed_date=mixed_date,
        location_mixed=location_mixed,
        location_exported=location_exported,
        genre=genre,
        comments=comments,
        formatted_comments=formatted_comments,
        num_multitracks=num_multitracks
    )


@APP.route('/uploadform')
def upload_form():
    """
    Renders upload.html
    """

    ticket_number = request.args.get('ticket_number')
    return render_template(
        'upload.html', upload_url='upload?ticket_number={}'.format(ticket_number))


@APP.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Uploads a file to the upload folder from the upload.html page
    """
    if request.method == 'POST':
        ticket_number = request.args.get('ticket_number')
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        requested_file = request.files['file']
        if requested_file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if requested_file and allowed_file(requested_file.filename):
            file_ext = requested_file.filename.rsplit('.', 1)[1]
            file_save_name = 'signedform_ticket_{}.{}'.format(
                ticket_number, file_ext
            )
            file_save_path = os.path.join(
                APP.config['UPLOAD_FOLDER'], file_save_name
            )
            requested_file.save(file_save_path)

            send_mail(
                APP, MAIL, 
                "medleydbaccess@gmail.com",
                "[form upload] Creative Commons Consent Form | MeldeyDB Manager",
                " ",
                attachment=file_save_path
            )

        return redirect(url_for('thankyou'))


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description="medleydb_webapp"
        )
    PARSER.add_argument("password", type=str, help="medleydb gmail password")
    PARSER.add_argument(
        "--debug", action="store_const", const=True, default=False
    )
    ARGS = PARSER.parse_args()
    APP.config.update(dict(MAIL_PASSWORD=ARGS.password))

    MAIL = Mail(APP)

    APP.run(port=5080, host='0.0.0.0', debug=ARGS.debug)


