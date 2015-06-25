__author__ = 'Marko Milutinovic'

import unittest
from array import array

from Dekompressor import Dekompressor
from SimpleDecoder import SimpleDecoder

class KompressorTests(unittest.TestCase):
    def test_constructor(self):
        """
        Purpose: Instantiate an object
        Expectation: The member variables should be initialized correctly
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        self.assertEqual(256, dekompressor.mSectionSize)
        self.assertEqual(0, dekompressor.mSpecialSymbol1)
        self.assertEqual(3, dekompressor.mSpecialSymbol1MaxRun)
        self.assertEqual(257, dekompressor.mSpecialSymbol1RunLengthStart)
        self.assertEqual(0xFF, dekompressor.mSpecialSymbol2)
        self.assertEqual(4, dekompressor.mSpecialSymbol2MaxRun)
        self.assertEqual(260, dekompressor.mSpecialSymbol2RunLengthStart)
        self.assertEqual(10, dekompressor.mGenericMaxRun)
        self.assertEqual(264, dekompressor.mGenericRunLengthStart)
        self.assertEqual(257+3+4+10, dekompressor.mVocabularySize)
        self.assertEqual(1, dekompressor.mBWTransformStoreBytes)
        self.assertNotEqual(None, dekompressor.mSectionTransformData)
        self.assertEqual(257, len(dekompressor.mSectionTransformData))
        self.assertEqual(257, dekompressor.mSectionTransformDataMaxSize)
        self.assertNotEqual(None, dekompressor.mDecoder)
        self.assertEqual(False, dekompressor.mContinuousModeEnabled)
        self.assertEqual(0, dekompressor.mContinuousModeTotalData)
        self.assertEqual(0, dekompressor.mContinuousModeDataDecompressed)

    def test_expandRunsSpecific_no_data(self):
        """
        Purpose: Pass in array with no data
        Expectation: 0 data should be expanded
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [])
        expandedData = array('i', [0]*32)

        expandedCount = dekompressor._expandRunsSpecific(0, 257, 3, compressedData, 0, expandedData, 20)

        self.assertEqual(0, expandedCount)

    def test_expandRunsSpecific_small_set(self):
        """
        Purpose: Pass in small array to be decoded which has expansion symbols at beginning and end
        Expectation: The data should be expanded correctly
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [257, 2, 0, 4, 260])
        expandedData = array('i', [0]*32)

        expandedCount = dekompressor._expandRunsSpecific(0, 257, 3, compressedData, 5, expandedData, 20)

        self.assertEqual(10, expandedCount)
        self.assertEqual(0, expandedData[0])
        self.assertEqual(0, expandedData[1])
        self.assertEqual(2, expandedData[2])
        self.assertEqual(0, expandedData[3])
        self.assertEqual(4, expandedData[4])
        self.assertEqual(0, expandedData[5])
        self.assertEqual(0, expandedData[6])
        self.assertEqual(0, expandedData[7])
        self.assertEqual(0, expandedData[8])
        self.assertEqual(0, expandedData[9])

    def test_expandRunsSpecific_larger_data_set(self):
        """
        Purpose: Pass in array to be decoded with expansion symbol at the end
        Expectation: The data should be expanded correctly
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [1, 2, 260, 5, 6, 7, 259, 259, 260, 260, 257, 8, 9, 0, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        expandedData = array('i', [0]*64)

        expandedCount = dekompressor._expandRunsSpecific(0, 257, 3, compressedData, 27, expandedData, 64)

        self.assertEqual(46, expandedCount)
        self.assertEqual(1, expandedData[0])
        self.assertEqual(2, expandedData[1])
        self.assertEqual(0, expandedData[2])
        self.assertEqual(0, expandedData[3])
        self.assertEqual(0, expandedData[4])
        self.assertEqual(0, expandedData[5])
        self.assertEqual(0, expandedData[6])
        self.assertEqual(5, expandedData[7])
        self.assertEqual(6, expandedData[8])
        self.assertEqual(7, expandedData[9])
        self.assertEqual(0, expandedData[10])
        self.assertEqual(0, expandedData[11])
        self.assertEqual(0, expandedData[12])
        self.assertEqual(0, expandedData[13])
        self.assertEqual(0, expandedData[14])
        self.assertEqual(0, expandedData[15])
        self.assertEqual(0, expandedData[16])
        self.assertEqual(0, expandedData[17])
        self.assertEqual(0, expandedData[18])
        self.assertEqual(0, expandedData[19])
        self.assertEqual(0, expandedData[20])
        self.assertEqual(0, expandedData[21])
        self.assertEqual(0, expandedData[22])
        self.assertEqual(0, expandedData[23])
        self.assertEqual(0, expandedData[24])
        self.assertEqual(0, expandedData[25])
        self.assertEqual(0, expandedData[26])
        self.assertEqual(0, expandedData[27])
        self.assertEqual(0, expandedData[28])
        self.assertEqual(0, expandedData[29])
        self.assertEqual(8, expandedData[30])
        self.assertEqual(9, expandedData[31])
        self.assertEqual(0, expandedData[32])
        self.assertEqual(1, expandedData[33])
        self.assertEqual(1, expandedData[34])
        self.assertEqual(2, expandedData[35])
        self.assertEqual(0, expandedData[36])
        self.assertEqual(0, expandedData[37])
        self.assertEqual(0, expandedData[38])
        self.assertEqual(0, expandedData[39])
        self.assertEqual(0, expandedData[40])
        self.assertEqual(0, expandedData[41])
        self.assertEqual(0, expandedData[42])
        self.assertEqual(0, expandedData[43])
        self.assertEqual(0, expandedData[44])
        self.assertEqual(0, expandedData[45])

    def test_expandRunsSpecific_symbol_below_expansion_range(self):
        """
        Purpose: Pass in data that has an extended symbol that is greater than 255 but less than expansion symbol range
        Expectation: An exception should be thrown
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [256, 2, 0, 4, 260])
        expandedData = array('i', [0]*32)

        with self.assertRaises(Exception):
            expandedCount = dekompressor._expandRunsSpecific(0, 257, 3, compressedData, 5, expandedData, 20)

    def test_expandRunsSpecific_symbol_above_expansion_range(self):
        """
        Purpose: Pass in data that has an extended symbol that is greater than expansion symbol range
        Expectation: An exception should be thrown
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [256, 2, 0, 4, 264])
        expandedData = array('i', [0]*32)

        with self.assertRaises(Exception):
            expandedCount = dekompressor._expandRunsSpecific(0, 257, 3, compressedData, 5, expandedData, 20)

    def test_expandRunsSpecific_extended_symbol_overflow(self):
        """
        Purpose: Pass in data that has an extended symbol that ends up overflowing the outgoing array
        Expectation: An exception should be thrown
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [257, 2, 0, 4, 260])
        expandedData = array('i', [0]*8)

        with self.assertRaises(Exception):
            expandedCount = dekompressor._expandRunsSpecific(0, 257, 3, compressedData, 5, expandedData, 8)

    def test_expandRunsSpecific_normal_symbol_overflow(self):
        """
        Purpose: Pass in data that has a normal symbol that ends up overflowing the outgoing array
        Expectation: An exception should be thrown
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [257, 2, 0, 4, 2])
        expandedData = array('i', [0]*5)

        with self.assertRaises(Exception):
            expandedCount = dekompressor._expandRunsSpecific(0, 257, 3, compressedData, 5, expandedData, 5)

    def test_expandRunsGeneric_first_symbol_out_of_bounds(self):
        """
        Purpose: Pass in data that starts with a symbol out of bounds
        Expectation: An exception should be thrown
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [257, 2, 0, 4, 2])
        expandedData = array('i', [0]*5)

        with self.assertRaises(Exception):
            expandedCount = dekompressor._expandRunsGeneric(257, 3, compressedData, 5, expandedData, 5)

    def test_genericRunsGeneric_no_data(self):
        """
        Purpose: Pass in array with no data
        Expectation: 0 data should be expanded
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [])
        expandedData = array('i', [0]*32)

        expandedCount = dekompressor._expandRunsGeneric(257, 3, compressedData, 0, expandedData, 20)

        self.assertEqual(0, expandedCount)

    def test_expandRunsGeneric_small_set(self):
        """
        Purpose: Pass in small array to be decoded which has expansion symbols at beginning and end
        Expectation: The data should be expanded correctly
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [1, 257, 2, 0, 4, 260, 260, 257])
        expandedData = array('i', [0]*32)

        expandedCount = dekompressor._expandRunsGeneric(257, 3, compressedData, 8, expandedData, 20)

        self.assertEqual(14, expandedCount)
        self.assertEqual(1, expandedData[0])
        self.assertEqual(1, expandedData[1])
        self.assertEqual(2, expandedData[2])
        self.assertEqual(0, expandedData[3])
        self.assertEqual(4, expandedData[4])
        self.assertEqual(4, expandedData[5])
        self.assertEqual(4, expandedData[6])
        self.assertEqual(4, expandedData[7])
        self.assertEqual(4, expandedData[8])
        self.assertEqual(4, expandedData[9])
        self.assertEqual(4, expandedData[10])
        self.assertEqual(4, expandedData[11])
        self.assertEqual(4, expandedData[12])
        self.assertEqual(4, expandedData[13])

    def test_expandRunsGeneric_larger_data_set(self):
        """
        Purpose: Pass in array to be decoded with expansion symbol at the end
        Expectation: The data should be expanded correctly
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [1, 2, 260, 5, 6, 7, 259, 259, 260, 260, 257, 8, 9, 0, 1, 1, 2, 0, 0, 0, 258, 0, 0, 0, 0, 0, 258])
        expandedData = array('i', [0]*64)

        expandedCount = dekompressor._expandRunsGeneric(257, 3, compressedData, 27, expandedData, 64)

        self.assertEqual(42, expandedCount)
        self.assertEqual(1, expandedData[0])
        self.assertEqual(2, expandedData[1])
        self.assertEqual(2, expandedData[2])
        self.assertEqual(2, expandedData[3])
        self.assertEqual(2, expandedData[4])
        self.assertEqual(2, expandedData[5])
        self.assertEqual(5, expandedData[6])
        self.assertEqual(6, expandedData[7])
        self.assertEqual(7, expandedData[8])
        self.assertEqual(7, expandedData[9])
        self.assertEqual(7, expandedData[10])
        self.assertEqual(7, expandedData[11])
        self.assertEqual(7, expandedData[12])
        self.assertEqual(7, expandedData[13])
        self.assertEqual(7, expandedData[14])
        self.assertEqual(7, expandedData[15])
        self.assertEqual(7, expandedData[16])
        self.assertEqual(7, expandedData[17])
        self.assertEqual(7, expandedData[18])
        self.assertEqual(7, expandedData[19])
        self.assertEqual(7, expandedData[20])
        self.assertEqual(7, expandedData[21])
        self.assertEqual(7, expandedData[22])
        self.assertEqual(7, expandedData[23])
        self.assertEqual(8, expandedData[24])
        self.assertEqual(9, expandedData[25])
        self.assertEqual(0, expandedData[26])
        self.assertEqual(1, expandedData[27])
        self.assertEqual(1, expandedData[28])
        self.assertEqual(2, expandedData[29])
        self.assertEqual(0, expandedData[30])
        self.assertEqual(0, expandedData[31])
        self.assertEqual(0, expandedData[32])
        self.assertEqual(0, expandedData[33])
        self.assertEqual(0, expandedData[34])
        self.assertEqual(0, expandedData[35])
        self.assertEqual(0, expandedData[36])
        self.assertEqual(0, expandedData[37])
        self.assertEqual(0, expandedData[38])
        self.assertEqual(0, expandedData[39])
        self.assertEqual(0, expandedData[40])
        self.assertEqual(0, expandedData[41])

    def test_expandRunsGeneric_symbol_below_expansion_range(self):
        """
        Purpose: Pass in data that has an extended symbol that is greater than 255 but less than expansion symbol range
        Expectation: An exception should be thrown
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [256, 2, 0, 4, 260])
        expandedData = array('i', [0]*32)

        with self.assertRaises(Exception):
            expandedCount = dekompressor._expandRunsGeneric(257, 3, compressedData, 5, expandedData, 20)

    def test_expandRunsGeneric_symbol_above_expansion_range(self):
        """
        Purpose: Pass in data that has an extended symbol that is greater than expansion symbol range
        Expectation: An exception should be thrown
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [256, 2, 0, 4, 264])
        expandedData = array('i', [0]*32)

        with self.assertRaises(Exception):
            expandedCount = dekompressor._expandRunsGeneric(257, 3, compressedData, 5, expandedData, 20)

    def test_expandRunsGeneric_extended_symbol_overflow(self):
        """
        Purpose: Pass in data that has an extended symbol that ends up overflowing the outgoing array
        Expectation: An exception should be thrown
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [1, 257, 0, 4, 260])
        expandedData = array('i', [0]*8)

        with self.assertRaises(Exception):
            expandedCount = dekompressor._expandRunsGeneric(257, 3, compressedData, 5, expandedData, 6)

    def test_expandRunsGeneric_normal_symbol_overflow(self):
        """
        Purpose: Pass in data that has a normal symbol that ends up overflowing the outgoing array
        Expectation: An exception should be thrown
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [1, 257, 2, 0, 4, 2])
        expandedData = array('i', [0]*5)

        with self.assertRaises(Exception):
            expandedCount = dekompressor._expandRunsGeneric(257, 3, compressedData, 5, expandedData, 5)

    def test_reverseBWTransformBasic(self):
        """
        Purpose:
        Expectation:
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        preTransformData = array('i', [1, 257, 2, 0, 4, 2])
        restoredData = array('i', [0]*32)

        restoreDataLen = dekompressor._reverseBWTransform(preTransformData, 6, restoredData, 32)


if __name__ == '__main__':
    unittest.main()
