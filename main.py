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
def status():
    """return status"""
    return str({
            "insert": False,
            "fetch": False,
            "delete": False,
            "list": False
            })


@app.route('/api/capital/<id>', methods=['POST', 'GET', 'DELETE'])
def access_capitals():
    """inserts and retrieves notes from datastore"""

    book = capital.Capital()
    if request.method == 'GET':
        results = book.fetch_notes()
        result = [capital.parse_note_time(obj) for obj in results]
        return jsonify(result)
    elif request.method == 'POST':
        print json.dumps(request.get_json())
        text = request.get_json()['text']
        book.store_note(text)
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
