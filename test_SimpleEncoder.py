__author__ = 'Marko Milutinovic'

import unittest
import SimpleEncoder
from array import *

class TestSimpleEncoder(unittest.TestCase):
    def test_constructor(self):
        """
        Purpose: Instantiate object
        Expectation: All member variables should be set to defaults
        :return:
        """
        encoder = SimpleEncoder.SimpleEncoder(261)

        self.assertEqual(261, encoder.mVocabularySize)
        self.assertNotEqual(None, encoder.mEncodedData)

    def test_encode_input_data_too_small(self):
        """
        Purpose: Pass in integer array of symbols to be encoded that is smaller than the length provided
        Expectation; Exception should be raised
        :return:
        """
        encoder = SimpleEncoder.SimpleEncoder(256)

        dataToEncode = array('i', [])
        encodedData = bytearray(20)

        with self.assertRaises(Exception):
            encoder.encode(dataToEncode, 40, encodedData, 20)

    def test_encode_output_data_too_small(self):
        """
        Purpose: Pass in output byte array that is smaller than the length provided
        Expectation; Exception should be raised
        :return:
        """
        encoder = SimpleEncoder.SimpleEncoder(256)

        dataToEncode = array('i', [])
        encodedData = bytearray(20)

        with self.assertRaises(Exception):
            encoder.encode(dataToEncode, 20, encodedData, 21)

    def test_encode_small_set(self):
        """
        Purpose: Pass in byte array to encode
        Expectation; Data should be stored in the test array
        :return:
        """
        encoder = SimpleEncoder.SimpleEncoder(256)

        dataToEncode = array('i', [])
        dataToEncode.append(1)
        dataToEncode.append(2)
        dataToEncode.append(2)
        dataToEncode.append(4)
        dataToEncode.append(77)

        encodedData = bytearray(20)

        self.assertEqual(5, encoder.encode(dataToEncode, 5, encodedData, 20))
        self.assertEqual(1, encoder.mEncodedData[0])
        self.assertEqual(2, encoder.mEncodedData[1])
        self.assertEqual(2, encoder.mEncodedData[2])
        self.assertEqual(4, encoder.mEncodedData[3])
        self.assertEqual(77, encoder.mEncodedData[4])

    def test_encode_invalid_symbol(self):
        """
        Purpose: Pass in byte array to encode with a symbol that is out of range
        Expectation; An exception should be thrown
        :return:
        """
        encoder = SimpleEncoder.SimpleEncoder(256)

        dataToEncode = array('i', [])
        dataToEncode.append(1)
        dataToEncode.append(2)
        dataToEncode.append(2)
        dataToEncode.append(4)
        dataToEncode.append(257)

        encodedData = bytearray(20)

        with self.assertRaises(Exception):
            encoder.encode(dataToEncode, 5, encodedData, 20)

if __name__ == '__main__':
    unittest.main()
