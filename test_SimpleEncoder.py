__author__ = 'Marko Milutinovic'

import unittest
import SimpleEncoder

class TestSimpleEncoder(unittest.TestCase):
    def test_constructor(self):
        """
        Purpose: Instantiate object
        Expectation: All member variables should be set to defaults
        :return:
        """
        encoder = SimpleEncoder.SimpleEncoder(5)

        self.assertEqual(261, encoder.mVocabularySize)
        self.assertNotEqual(None, encoder.mEncodedData)
        self.assertEqual(0, encoder.mSymbolCount)

    def test_encode(self):
        """
        Purpose: Pass in symbols to be encoded
        Expectation; The symbol should be appended to the integer array and the count should be incremented
        :return:
        """
        encoder = SimpleEncoder.SimpleEncoder(5)

        encoder.encode(2)
        encoder.encode(251)
        encoder.encode(252)

        self.assertEqual(3, encoder.mSymbolCount)
        self.assertEqual(2, encoder.mEncodedData[0])
        self.assertEqual(251, encoder.mEncodedData[1])
        self.assertEqual(252, encoder.mEncodedData[2])

    def test_getEncodedData(self):
        """
        Purpose: Get the encoded data.
        Expectation: The function will not add any data to output data byte array. The count will be returned
        :return:
        """

        encoder = SimpleEncoder.SimpleEncoder(5)

        encoder.encode(2)
        encoder.encode(251)
        encoder.encode(252)

        self.assertEqual(3, encoder.mSymbolCount)
        self.assertEqual(2, encoder.mEncodedData[0])
        self.assertEqual(251, encoder.mEncodedData[1])
        self.assertEqual(252, encoder.mEncodedData[2])

        data = bytearray(12)
        self.assertEqual(3, encoder.getEncodedData())

if __name__ == '__main__':
    unittest.main()
