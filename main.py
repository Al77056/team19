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
    tel = {'delete': True, 'fetch': True, 'insert': True, 'list': True, "query": True, "search": True, "pubsub": True, "storage": True}
    return jsonify(tel), 200

@app.route('/api/capitals', methods=['GET'])
def getCaptials():
    """Get all capitals with optional query string"""
    query_strings = request.args.get('query')
    search_strings = request.args.get('search')
    book = capital.Capital()
    result = book.fetch_capitals(query_strings, search_strings)
    return jsonify(result), 200

@app.route('/api/capitals/<id>', methods=['PUT', 'GET', 'DELETE'])
def access_capitals(id):
    """inserts and retrieves notes from datastore"""

    book = capital.Capital()
    if request.method == 'GET':
        result = book.fetch_capital(id)
        if len(result):
            return jsonify(result[0]), 200
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

@app.route('/api/capitals/<int:id>/store', methods=['POST'])
def store_capitals(id):
    try:
        text = request.get_json()
        if not text or not text.has_key('bucket'):
            return jsonify({"code": 0, "message": "Bucket name is not specified"}), 404
        bucket = text['bucket']
        book = capital.Capital()
        success = book.save_capital_to_bucket(id, bucket)
        if success:
            return 'Successfully stored in GCS', 200
        else:
            return jsonify({"code": 0, "message": "Capital record not found"}), 404
    except Exception as ex:
        utility.log_info(ex.message)
        return jsonify({"code": 0, "message": "Unexpected error"}), 500

@app.route('/api/capitals/<id>/publish', methods=['POST'])
def publish_capitals_record(id):
    try:
        book = capital.Capital()
        text = request.get_json()
        success = book.fetch_capital(id)
        if success:
            msgId = book.publish_toPubSub(text['topic'], id)
            return jsonify({"messageId": msgId}), 200
        else:
            return jsonify({"code": 0, "message": "Capital record not found"}), 404
    except Exception as e:
        logging.exception('Oops! 500!!')
        return jsonify({"code": 0, "message": "Unexpected error"}), 500

@app.route('/pubsub/receive', methods=['POST'])
def pubsub_receive():
    """dumps a received pubsub message to the log"""

    data = {}
    try:
        obj = request.get_json()
        utility.log_info(json.dumps(obj))

        data = base64.b64decode(obj['message']['data'])
        utility.log_info(data)

    except Exception as e:
        # swallow up exceptions
        logging.exception('Oops!')

    return jsonify(data), 200

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
