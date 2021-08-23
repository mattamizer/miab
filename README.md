# miab

Message in a bottle

This is an implementation of a Flask app for interacting with files stored in memcached. 

## Setup

**NOTE**: It is assumed that you have Python 3 installed on your system. If that's not the case please install Python 3 before running the script. I recommend checking out [pyenv](https://github.com/pyenv/pyenv).

In order to get started you'll need to install the project dependencies.

1. Create and activate a virtual environment and
2. Install the project dependencies via `pip`

All you have to do is run `make install` and you'll be good to go.

## Running the app

Starting the app is done via the Makefile by running `make run`. This will bring the Flask app up on port 5000 and start the memcached docker container. The container will automatically download if you don't have it locally.

## Interacting with the app

This app has been designed to be interacted with from the CLI using RESTful principals. There is a UI on port 5000 for convenience but it doesn't do much. There are three routes that the app exposes.

1. The root path at `/` which serves information about the API
2. The storage path at `/store` which accepts a JSON payload and stores the data contained in the value field. The key in the JSON is used as the storage key.
3. The retrieval path at `/retrieve?key=<YOUR KEY>` which takes a query string named `key` whose value is the key under which the data you'd like is stored

### Examples

These examples use [HTTPie](https://httpie.io/) as it provides some nice shorthand for requests that `curl` does not.

#### POST

Assuming there is a file called `test.txt` on your filesystem run the following:
`http :5000/store bar=@test.txt`

Example response:
```
HTTP/1.0 200 OK
Content-Length: 19
Content-Type: text/html; charset=utf-8
Date: Mon, 23 Aug 2021 17:41:45 GMT
Server: Werkzeug/2.0.1 Python/3.8.5

Stored with key bar
```

#### GET

Each endpoint on the server allows for get but all have different return values. Each will be outlined below.

Examples:

Root path `/`:

To get the root path run the following:
`http :5000`

Example response:
```
HTTP/1.0 200 OK
Content-Length: 517
Content-Type: text/html; charset=utf-8
Date: Mon, 23 Aug 2021 17:44:30 GMT
Server: Werkzeug/2.0.1 Python/3.8.5

<pre>
    Welcome to Message in a Bottle! It's a Flask app for storing and retrieving files. Some rules:

    * Files **must** be between 0 and 50 megabytes
    * File names must **not** contain spaces or control characters
    * Files should be submitted one at a time, not in a batch/list

    GET / - You are here
    POST /store - store the file in memcached. Accepts JSON data of the form {"filename": "contents of file"}
    GET /retrieve?key=<filename> - get the file named <filename> from the cache
    </pre>
```

Storage path `/store`:

Run the following:
`http :5000/store`

Example response:
```
HTTP/1.0 200 OK
Content-Length: 99
Content-Type: text/html; charset=utf-8
Date: Mon, 23 Aug 2021 17:50:37 GMT
Server: Werkzeug/2.0.1 Python/3.8.5

    Try using `curl` to send a request to me! Make sure it's using 'Accept: application/json'
```

The real work is done on the `/retrieve?key=<KEY>` endpoint.

Assuming you have stored an item with the key `bar` run the following:
`http :5000/retrieve key==bar`

Example response:
```
HTTP/1.0 200 OK
Content-Length: 38
Content-Type: text/html; charset=utf-8
Date: Mon, 23 Aug 2021 17:53:51 GMT
Server: Werkzeug/2.0.1 Python/3.8.5

/Users/mmorri929/code/miab/output.txt
```

## Running the tests

In order to run the tests simply run `make test`.
