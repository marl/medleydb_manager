"""
Main webapp.py function
"""
#!/usr/bin/env python
import os
import time
import argparse
import numpy
from flask import Flask, jsonify, render_template, request, flash, redirect
from flask import url_for
from flask_mail import Mail

from utils import connect_db, get_header, send_mail
from utils import fill_table, format_headers, allowed_file
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
    db_connection = connect_db(APP)
    cursor = db_connection.execute('select * from tickets')
    tickets_headers = get_header(APP, 'tickets')

    tickets = {}
    for name in tickets_headers:
        tickets[name] = []

    tickets['url'] = []
    for row in cursor:
        for name, item in zip(tickets_headers, row):
            tickets[name].append(item)
        tickets['url'].append('/ticket?id={}'.format(row[0]))

    formatted_tickets_headers = [format_headers(h) for h in tickets_headers]

    return render_template(
        'viewtickets.html', tickets=tickets,
        db_tickets_headers=tickets_headers,
        formatted_tickets_headers=formatted_tickets_headers
    )


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
    db_connection = connect_db(APP)
    ticket_status_headers = get_header(APP, 'tickets')
    ticket_history_headers = get_header(APP, 'ticket_history')
    multitracks_in_ticket_headers = get_header(APP, 'multitracks')

    formatted_ticket_status_headers = [
        format_headers(h) for h in ticket_status_headers
    ]
    formatted_ticket_history_headers = [
        format_headers(h) for h in ticket_history_headers
    ]
    formatted_multitracks_in_ticket_headers = [
        format_headers(h) for h in multitracks_in_ticket_headers
    ]

    ticket_status_cursor = db_connection.execute(
        'select * from tickets where ticket_number="{}"'.format(ticket_id)
    )
    ticket_history_cursor = db_connection.execute(
        'select * from ticket_history where ticket_number="{}"'.format(
            ticket_id
        )
    )
    multitracks_cursor = db_connection.execute(
        'select * from multitracks where ticket_number="{}"'.format(ticket_id)
    )

    tickets = fill_table(ticket_status_headers, ticket_status_cursor)
    ticket_history = fill_table(ticket_history_headers, ticket_history_cursor)
    multitracks_in_ticket = fill_table(
        multitracks_in_ticket_headers, multitracks_cursor
    )

    multitracks_in_ticket['url'] = []
    multitracks_cursor = db_connection.execute(
        'select * from multitracks where ticket_number="{}"'.format(ticket_id)
    )
    for row in multitracks_cursor:
        multitracks_in_ticket['url'].append('/multitrack?id={}'.format(row[2]))

    return render_template(
        'ticket.html', ticket_id=ticket_id,
        db_ticket_status_headers=ticket_status_headers,
        formatted_ticket_status_headers=formatted_ticket_status_headers,
        db_ticket_history_headers=ticket_history_headers,
        formatted_ticket_history_headers=formatted_ticket_history_headers,
        db_multitracks_in_ticket_headers=multitracks_in_ticket_headers,
        formatted_multitracks_in_ticket_headers=formatted_multitracks_in_ticket_headers,
        tickets=tickets,
        ticket_history=ticket_history,
        multitracks_in_ticket=multitracks_in_ticket
    )

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
    formatted_mtrack_history_headers: list
        formatted headers of multitrack history table
    multitrack_history: dictionary
        contents in multitrack history table
    multitrack_status: dictionary
        contents in multitrack status table

    """

    multitrack_id = request.args.get('id')
    db_connection = connect_db(APP)

    multitrack_status_headers = get_header(APP, 'multitracks')
    multitrack_history_headers = get_header(APP, 'multitrack_history')

    formatted_multitrack_status_headers = [
        format_headers(h) for h in multitrack_status_headers
    ]
    formatted_mtrack_history_headers = [
        format_headers(h) for h in multitrack_history_headers
    ]

    multitrack_status_cursor = db_connection.execute(
        'select * from multitracks where multitrack_id="{}"'.format(
            multitrack_id
        )
    )
    multitrack_history_cursor = db_connection.execute(
        'select * from multitrack_history where multitrack_id="{}"'.format(
            multitrack_id
        )
    )

    multitrack_status = fill_table(
        multitrack_status_headers, multitrack_status_cursor
    )
    multitrack_history = fill_table(
        multitrack_history_headers, multitrack_history_cursor
    )

    return render_template(
        'multitrack.html', multitrack_id=multitrack_id,
        db_multitrack_status_headers=multitrack_status_headers,
        formatted_multitrack_status_headers=formatted_multitrack_status_headers,
        db_multitrack_history_headers=multitrack_history_headers,
        formatted_mtrack_history_headers=formatted_mtrack_history_headers,
        multitrack_history=multitrack_history,
        multitrack_status=multitrack_status
    )


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
    return render_template(
        'newticket_multitracks.html', 
        multitrack_number=multitrack_number, 
        total_multitracks=total_multitracks
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


@APP.route('/api/requestrecord')
def requestrecord_api():
    """
    API for requestrecord.html.
    """

    date_opened = time.strftime("%x")
    date_updated = time.strftime("%x")
    your_name = request.args.get('your_name')
    your_email = request.args.get('your_email')
    contact_name = request.args.get('contact_name')
    contact_email = request.args.get('contact_email')
    record_date1 = request.args.get('record_date1')
    record_date2 = request.args.get('record_date2')
    record_date3 = request.args.get('record_date3')
    hours_needed = request.args.get('hours_needed')
    expected_num = request.args.get('expected_num')
    genre = request.args.get('genre')

    # add code to add row to tickets and ticket_history tables
    db_connection = connect_db(APP)

    ticket_number_cursor = db_connection.execute(
        "select ticket_number from tickets"
    )
    ticket_numbers = [int(t[0]) for t in ticket_number_cursor]
    ticket_number = numpy.max(ticket_numbers) + 1

    db_connection.execute(
        'insert into tickets values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
            ticket_number, "Requested", None, date_opened, date_updated, None,
            None, None, your_name, your_email, "Julia Caruso",
            "julia.caruso@nyu.edu", genre, expected_num, None)
    )

    db_connection.execute(
        'insert into ticket_history values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
            ticket_number, "Requested", None, date_opened, date_updated, None,
            None, None, your_name, your_email, "Julia Caruso",
            "julia.caruso@nyu.edu", genre, expected_num, None)
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
            your_name, your_email, contact_name, contact_email, record_date1,
            record_date2, record_date3, hours_needed, expected_num
        ),
        attachment=None
    )

    return str(ticket_number)


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
    db_connection = connect_db(APP)

    ticket_number_cursor = db_connection.execute(
        "select ticket_number from tickets"
    )
    ticket_numbers = [int(t[0]) for t in ticket_number_cursor]
    ticket_number = numpy.max(ticket_numbers) + 1

    db_connection.execute(
        'insert into tickets values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
        ticket_number, status, ticket_name, date_opened, date_updated,
        session_date, engineer_name, engineer_email, your_name, your_email,
        assignee_name, assignee_email, genre, num_multitracks, comments)
    )

    db_connection.execute(
        'insert into ticket_history values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
        ticket_number, status, ticket_name, 
        date_opened, date_updated, session_date, engineer_name,
        engineer_email, creator_name, creator_email, assignee_name,
        assignee_email, genre, num_multitracks, comments))

    db_connection.commit()


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

    db_connection = connect_db(APP)

    # code to add row to multitracks and multitrack_history tables in database
    db_connection.execute('insert into multitracks_in_ticket values("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format(
        ticket_number, status, multitrack_id, date_opened, date_updated, 
        artist_name, multitrack_name, genre, num_instruments,
        your_name, your_email, engineer_name, engineer_email, 
        mixer_name, mixer_email, bouncer_name, bouncer_email, comments))

    db_connection.execute('insert into multitrack_history values("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
        ticket_number, status, multitrack_id,
        date_opened, date_updated, artist_name, multitrack_name, genre,
        num_instruments, your_name, your_email, engineer_name, engineer_email, 
        mixer_name, mixer_email, bouncer_name, bouncer_email, comments))

    db_connection.commit()

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


@APP.route('/uploadform')
def upload_form():
    ticketnumber = request.args.get('ticketnumber')
    return render_template(
        'upload.html', upload_url='upload?ticketnumber={}'.format(ticketnumber))


@APP.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        ticket_number = request.args.get('ticketnumber')
        print ticket_number
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
                APP, MAIL, "MedleyD.taea5mqvehv6g5ij@u.box.com",
                " ", " ", attachment=file_save_path
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


