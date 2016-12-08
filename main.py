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
    tel = {'delete': True, 'fetch': True, 'insert': True, 'list': True, "query": False, "search": False, "pubsub": False, "storage": False}
    return jsonify(tel), 200

@app.route('/api/capitals', methods=['GET'])
def access_all_capitals():
    """Get all capitals"""
    book = capital.Capital()
    result = book.fetch_allCapitals()
    return jsonify(result), 200

@app.route('/api/capitals/<id>', methods=['PUT', 'GET', 'DELETE'])
def access_capitals(id):
    """inserts and retrieves notes from datastore"""

    book = capital.Capital()
    if request.method == 'GET':
        result = book.fetch_capital(id)
        if len(result):
            return jsonify(result), 200
        else:
            return jsonify({"code": 0, "message": "Capital record not found"}), 404
    elif request.method == 'PUT':
        text = request.get_json()
        utility.log_info(text)
        book.store_capital(text, id)
        return "done", 200
    elif request.method == 'DELETE':
        success = book.delete_capital(id)
        if success:
            return "done", 200
        else:
            return jsonify({"code": 0, "message": "Capital record not found"}), 404

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
