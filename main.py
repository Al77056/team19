"""Main Entrypoint for the Application"""

import logging
import json
import base64

from flask import Flask, request
from flask import jsonify

import capital
import utility

app = Flask(__name__)


@app.route('/api/status')
def getStatus():
    """return status"""
    tel = {'delete': False, 'fetch': False, 'insert': False, 'list': False}
    return jsonify(tel);


@app.route('/api/capitals/<id>', methods=['PUT', 'GET', 'DELETE'])
def access_capitals(id):
    """inserts and retrieves notes from datastore"""

    book = capital.Capital()
    if request.method == 'GET':
        result = book.fetch_capital(id)
        return jsonify(result)
    elif request.method == 'PUT':
        text = request.get_json()
        utility.log_info(text)
        book.store_capital(text)
        return "done"


@app.errorhandler(500)
def server_error(err):
    """Error handler"""
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(err), 500


if __name__ == '__main__':
    # Used for running locally
    app.run(host='127.0.0.1', port=8080, debug=True)
