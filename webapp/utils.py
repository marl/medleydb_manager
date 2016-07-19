from flask_mail import Message, Mail
import sqlite3


def connect_db(app):
    """
    Creates and connects to an sqlite3 database that will hold the
    data of tickets and multitracks.

    Returns
    -------
    rv: database
    """
    db_connection = sqlite3.connect(app.config['DATABASE'])
    db_connection.row_factory = sqlite3.Row
    return db_connection


def get_header(app, table_name):
    """
    Retrieves headers from a table on the database

    Parameters
    ---------
    table_name: string

    Returns
    -------
    column_headers: list
    """
    db_connection = connect_db(app)
    cursor = db_connection.execute('select * from {}'.format(table_name))
    column_headers = list(map(lambda x: x[0], cursor.description))

    return column_headers


def send_mail(app, mail, recipients, subject, body, attachment=None):
    if not isinstance(recipients, list):
        recipients = [recipients]
    msg = Message(
        recipients=recipients,
        subject=subject,
        sender='medleydbaccess@gmail.com'
    )

    msg.body = body

    if attachment is not None:
        with app.open_resource(attachment) as fhandle:
            msg.attach(attachment, "image/pdf", fhandle.read())
    mail.send(msg)

    return True


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

def format_comments(comments):
    return comments.replace('"', "'")

def allowed_file(filename):
    file_ext = filename.rsplit('.', 1)[1]
    return '.' in filename and file_ext in ["pdf", "jpg", "jpeg", "png"]


