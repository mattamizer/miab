import hashlib
import logging
import os
from pathlib import Path

from pymemcache.client.base import Client
from pymemcache.exceptions import MemcacheIllegalInputError

from errors import errors

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

# Chunk data into 1 B segments
CHUNK_SIZE = 1024 * 1000
# Reject files over 50MB
MAX_FILE_SIZE = 1024 * 1024 * 50
# Location for temporary files
TEMP_FILE_LOC = "/tmp/{}"
# Create the memcached client, wait for reply from server before responding
client = Client("127.0.0.1", default_noreply=False)


def _read_file_chunks(fileObject):
    while True:
        data = fileObject.read(CHUNK_SIZE)
        if not data:
            break
        yield data


def write_temp_file(data, filename):
    log.info("Writing out a temp file for convenience")
    filepath = TEMP_FILE_LOC.format(filename)
    with open(filepath, "w") as tempfile:
        tempfile.write(data)
    return filepath


def get_temp_file(filename):
    log.info("Attempting to read the file {} from disk".format(filename))
    filepath = TEMP_FILE_LOC.format(filename)
    if os.path.exists(filepath):
        return open(filepath, "rb")
    else:
        raise errors.NoSuchKeyError(filename)


def chunk_data(file, filename):
    log.info("Chunking the data for caching using {} byte chunks".format(CHUNK_SIZE))
    chunked_data = {}
    key_iter = 0
    with open(file, "r") as test:
        log.debug("File contents are: {}".format(test.read()))
    test.close()
    readble = open(file, "r")
    for chunk in _read_file_chunks(readble):
        key = filename + str(key_iter)
        key_iter += 1
        chunked_data[key] = chunk
    readble.close()
    return chunked_data


def _check_evictions():
    stats = client.stats()
    if stats[b"evictions"] > 0:
        raise errors.EvictionsError


def check_file_size(file):
    log.info("Checking the file size")
    if os.stat(file).st_size > MAX_FILE_SIZE:
        log.error("File is too large for storage")
        raise errors.FileTooLargeError(file)
    return True


def generate_file_checksum(file):
    """Genenrate and store a file's MD5 hexdigest, raise an exception if the file already exists (checksum collision)"""
    log.info("Hashing the file contents")
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    f.close()
    return hash_md5.hexdigest()


def store_checksum(checksum, filename):
    # Use the checksum as the key so we can check for collisions.
    # The filename is the value so we know what the original file was called
    key = client.check_key(checksum)
    added = client.add(key, filename)
    if not added:
        log.error("The file contents already exist in the cache")
        raise errors.FileCollisionError(filename)
    # Also store the checksum for the file
    client.add(filename + "md5", checksum)
    return checksum


def check_valid_key(accessor):
    log.info("Checking if the cache key is valid")
    # We don't want bytes. Maybe we do but everything works with strings at present
    try:
        return client.check_key(accessor).decode()
    except MemcacheIllegalInputError:
        raise errors.InvalidKeyError(accessor)


def validate_contents(file, filename):
    result = client.get(filename + "md5").decode()
    log.debug("Result is {}".format(result))
    checksum = generate_file_checksum(file)
    log.debug("Checksum is {}".format(checksum))
    if result == checksum:
        return True
    else:
        log.error("Checksum mismatch, the stored data is corrupted")
        raise errors.CorruptDataError


def store_data(accessor, data):
    """
    Take in a data object of type bytes, chunk it, and store it
    """
    log.info("Attempting to store data in memcached")
    try:
        # Check if we're evicting things
        _check_evictions()
        # Chunk the data and use the accessor as the key
        store_checksum(generate_file_checksum(data), accessor)
        chunked_data = chunk_data(data, accessor)
        for key in chunked_data.keys():
            # Store the chunked data
            log.debug("Adding entry to cache with key {}".format(key))
            client.add(key, chunked_data[key])
        # Store how many chunks are in the key length so we can read it back later
        if not client.add(accessor, len(chunked_data.keys())):
            log.error("Key already exists in memcached")
            raise errors.KeyExistsError(accessor)
    # If we're evicting bail out, we don't want to accidentally lose more data
    except errors.EvictionsError:
        # Return false, we didn't store anything
        log.error("Ooops the cache is full and we're evicting data")
        return False
    except errors.FileCollisionError:
        # We've already got this file
        log.error("The file content already exist in the cache")
        raise errors.FileCollisionError(accessor)

    return accessor


def get_data(accessor):
    """
    Given the key accessor, find and return that value
    """
    # Find how many items we need to return
    log.info("Retrieving data from memcached")
    num_rows = client.get(accessor, default=b"not found").decode()
    if num_rows == "not found":
        raise errors.NoSuchKeyError(accessor)
    # Build the file from the response
    file_lines = []
    # Subtract one from the number of rows, since the actual keys will be one less than the length of the keys array
    for key in range(int(num_rows), 0, -1):
        cache_key = accessor + str(key - 1)
        file_lines.append(client.get(cache_key).decode())
    filepath = TEMP_FILE_LOC.format(str(accessor) + "read")
    with open(filepath, "w") as tempfile:
        tempfile.writelines(file_lines)
    tempfile.close()
    try:
        validate_contents(filepath, accessor)
    except errors.CorruptDataError:
        raise errors.CorruptDataError
    return Path(filepath).read_text()


def flush_cache():
    client.flush_all()
