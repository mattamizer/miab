import os
import logging
import random
import string
import unittest

from cache import memcached
from errors import errors


class TestCachingFunctionality(unittest.TestCase):
    def setUp(self):
        # Generate a 51 megabyte file
        self._generate_large_file(1024 * 1024 * 51, "toobig")
        # Generate a 50 megabyte file
        self._generate_large_file(1024 * 1024 * 50, "justright")
        # Disable all but debug logs
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        os.remove("toobig")
        os.remove("justright")
        memcached.flush_cache()
        logging.disable(logging.NOTSET)

    def _generate_large_file(self, filesize, filename):
        # Generate a file of <filesize> bytes and return it
        # Solution found at https://stackoverflow.com/questions/8816059/create-file-of-particular-size-in-python
        file = open(filename, "wb")
        file.seek(filesize - 1)
        file.write(b"\0")
        file.close()

    def _geneate_non_empty_file(self, filesize, filename):
        # Generate an array of random letters of size <filesize> bytes, then write them to a file
        chars = "".join(
            [random.choice(string.ascii_letters) for num in range(filesize)]
        )
        with open(filename, "w") as file:
            file.write(chars)

    def test_reject_large_file(self):
        with self.assertRaises(errors.FileTooLargeError):
            memcached.check_file_size("toobig")

    def test_fifty_is_ok(self):
        self.assertTrue(memcached.check_file_size("justright"))

    def test_checksum_generation(self):
        checksum = memcached.generate_file_checksum("justright")
        self.assertIsNotNone(checksum)
        # The result should be the same for the same file
        self.assertEqual(checksum, memcached.generate_file_checksum("justright"))

    def test_checksum_collision(self):
        checksum = memcached.generate_file_checksum("justright")
        self.assertIsNotNone(checksum)
        memcached.store_checksum(checksum, "goodstuff")
        collision = memcached.generate_file_checksum("justright")
        self.assertEqual(checksum, collision)
        with self.assertRaises(errors.FileCollisionError):
            memcached.store_checksum(collision, "oops")

    def test_file_chunking(self):
        # Generate a 3 megabytye file for testing chunks
        # This takes a while (seconds) so we do it inline
        self._geneate_non_empty_file(1024 * 1024 * 3, "chunky")
        foo = memcached.chunk_data("chunky", "testing")
        self.assertIsInstance(foo, dict)
        self.assertEqual(len(foo.keys()), 4)
        for key in foo.keys():
            self.assertIsInstance(foo[key], str)
        os.remove("chunky")

    def test_no_key(self):
        with self.assertRaises(errors.NoSuchKeyError):
            memcached.get_data("frob")

    def test_store_data(self):
        # Generate a 2 megabyte file for testing storing
        # This takes a while (seconds) so we do it inline
        self._geneate_non_empty_file(1024 * 1024 * 3, "storeme")
        test = memcached.store_data("key", "storeme")
        if not test:
            self.fail("Failed to store the data")
        self.assertEqual("key", test)

    def test_validate_data(self):
        # Generate a file, calculate & store the checksum, and validate that the same operation gives the same checksum
        self._geneate_non_empty_file(1024, "valid")
        checksum = memcached.generate_file_checksum("valid")
        self.assertIsNotNone(checksum)
        memcached.store_checksum(checksum, "validsum")
        self.assertTrue(memcached.validate_contents("valid", "validsum"))
        os.remove("valid")

    def test_get_data(self):
        self._geneate_non_empty_file(1024, "valid")
        test = memcached.store_data("testkey", "valid")
        if not test or test != "testkey":
            self.fail("Failed to store data")
        contents = memcached.get_data("testkey")
        self.assertIsNotNone(contents)


if __name__ == "__main__":
    unittest.main()
