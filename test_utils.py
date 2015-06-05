__author__ = 'marko'

import unittest
import utils


class TestUtils(unittest.TestCase):
   def test_getMinBytesToRepresent(self):
        # Purpose: Pass in varying max bytes values
        # Expectation: The correct number of bits to uniquely compress max bytes should be returned

        self.assertEqual(0, utils.getMinBytesToRepresent(0))
        self.assertEqual(1, utils.getMinBytesToRepresent(1))
        self.assertEqual(1, utils.getMinBytesToRepresent(2))
        self.assertEqual(1, utils.getMinBytesToRepresent(16))
        self.assertEqual(1, utils.getMinBytesToRepresent(50))
        self.assertEqual(1, utils.getMinBytesToRepresent(255))
        self.assertEqual(1, utils.getMinBytesToRepresent(256))
        self.assertEqual(2, utils.getMinBytesToRepresent(257))
        self.assertEqual(2, utils.getMinBytesToRepresent(2048))
        self.assertEqual(2, utils.getMinBytesToRepresent(2049))
        self.assertEqual(2, utils.getMinBytesToRepresent(10000))
        self.assertEqual(2, utils.getMinBytesToRepresent(65535))
        self.assertEqual(2, utils.getMinBytesToRepresent(65536))
        self.assertEqual(3, utils.getMinBytesToRepresent(200000))
        self.assertEqual(4, utils.getMinBytesToRepresent(65536000))
        self.assertEqual(4, utils.getMinBytesToRepresent(655360000))

   def test_calculateMaxBytes(self):
        # Purpose: Pass in varying word sizes
        # Expectation: The correct number of max bytes should be returned correctly

        self.assertEqual(0, utils.calculateMaxBytes(0))
        self.assertEqual(0, utils.calculateMaxBytes(1))
        self.assertEqual(0, utils.calculateMaxBytes(2))
        self.assertEqual(2, utils.calculateMaxBytes(3))
        self.assertEqual(512, utils.calculateMaxBytes(11))
        self.assertEqual(16384, utils.calculateMaxBytes(16))
        self.assertEqual(0, utils.calculateMaxBytes(50))

if __name__ == '__main__':
    unittest.main()
