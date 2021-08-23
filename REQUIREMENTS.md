# Deliverables

There are two deliverables for this project:

1. A library to store and retrieve files in Memcached.
1. An HTTP API that utilizes the library to store and retrieve files.

# Specs

## Library

- [X] Your library should be small and self-contained.
- [X] Your library should utilize a Memcached client, as well as any other libraries required.
- [X] Your library must accept any file size from 0 to 50 MB. It must reject files larger than 50 MB.
- [X] Your library must accept a file, chunk it, and store as bytes in Memcached with a minimum amount of overhead.
- [X] Your library must retrieve a file's chunks from Memcached and return a single stream of bytes.
- [X] Your library should chunk the file in any way appropriate.
- [X] Your library should key the chunks in any way appropriate.
- [X] Your library must check for file consistency to ensure the data retrieved is the same as the original data stored.
- [X] Your library must handle edge cases appropriately by raising an Exception or similar. Some examples of edge cases may include storing a file that already exists, trying to retrieve a file that does not exist, or when a file retrieved is inconsistent/corrupt.
- [X] Your library must have at least one test.
You can use this command to generate a 50 MB file of random data if needed: bash dd if=/dev/urandom of=bigoldfile.dat bs=1048576 count=50

## API

- [X] You should use your framework and language of choice in implementing your API (django, flask, etc.)
- [X] Your API should be a REST API.
- [X] Your API must accept a POST request with file contents in the payload and store it using your library. It may be convenient to return an identifier used for retrieval at a later time.
- [X] Your API must accept a GET request with a file name/identifier and retrieve it using your library. The file contents must be returned in the response.
- [X] Your API should appropriately handle edge cases (return an error response) when a file does not exist or is not consistent.
- [X] Your API must have at least one test.
