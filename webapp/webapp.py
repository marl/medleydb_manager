#!/usr/bin/env python
import os
import sys
import shutil
import logging
import tempfile
import operator

from flask import Flask, jsonify, render_template, request


APP = Flask(__name__)


@APP.route('/')
def index():
    # this loads the homepage
    myoptvars = 2
    return render_template('mywebsite.html', optvars=myoptvars)


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
