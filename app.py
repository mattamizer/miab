from flask import Flask
from flask import request
from flask import Response
import logging

from cache import memcached

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()
app = Flask(__name__)


@app.route("/")
def root():
    return """
    <pre>
    Welcome to Message in a Bottle! It's a Flask app for storing and retrieving files. Some rules:

    * Files **must** be between 0 and 50 megabytes
    * File names must **not** contain spaces or control characters
    * Files should be submitted one at a time, not in a batch/list

    GET / - You are here
    POST /store - store the file in memcached. Accepts JSON data of the form {"filename": "contents of file"}
    GET /retrieve?key=<filename> - get the file named <filename> from the cache
    </pre>
    """.strip()


@app.route("/store", methods=["GET", "POST"])
def store():
    if request.method == "POST":
        payload = request.get_json()
        log.debug(payload)
        for key in payload.keys():
            data = payload[key]
            try:
                memcached.check_valid_key(key)
                filepath = memcached.write_temp_file(data, key)
                memcached.check_file_size(filepath)
                memcached.store_data(key, filepath)
                return "Stored with key {}".format(key)
            except memcached.errors.FileTooLargeError as e:
                return Response(e.message, 413)
            except memcached.errors.KeyExistsError as e:
                return Response(e.message, 409)
            except memcached.errors.FileCollisionError as e:
                return Response(e.message, 409)
            except memcached.errors.InvalidKeyError as e:
                return Response(e.message, 400)
    return """
    Try using `curl` to send a request to me! Make sure it's using 'Accept: application/json'
    """


@app.route("/retrieve", methods=["GET"])
def retrieve():
    accessor = request.args.get("key")
    if not accessor:
        return Response("You must provide a key value to get data", 400)
    try:
        return Response(memcached.get_data(accessor), 200)
    except memcached.errors.NoSuchKeyError as e:
        return Response(e.message, 404)
    except memcached.errors.CorruptDataError:
        return Response("Stored data has been corrupted", 500)
