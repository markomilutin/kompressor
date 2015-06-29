__author__ = 'Marko Milutinovic'

import unittest
from array import array

from Dekompressor import Dekompressor
from SimpleEncoder import SimpleEncoder
from SimpleDecoder import SimpleDecoder
from Kompressor import Kompressor

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
        Purpose: Pass in data that has an extended symbol that is greater than max allowed
        Expectation: An exception should be thrown
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [256, 2, 0, 4, 300])
        expandedData = array('i', [0]*32)

        with self.assertRaises(Exception):
            expandedCount = dekompressor._expandRunsSpecific(0, 257, 3, compressedData, 5, expandedData, 20)

    def test_expandRunsSpecific_symbol_above_expansion_range(self):
        """
        Purpose: Pass in data that has an extended symbol that is greater than allowed range
        Expectation: An exception should be thrown
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        compressedData = array('i', [256, 2, 0, 4, 350])
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

    def test_reverseBWTransform_invalidData(self):
        """
        Purpose: Pass in data that is too small
        Expectation: An exception should be thrown
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        transforedData = array('i', [0])
        restoredData = array('i', [3])

        with self.assertRaises(Exception):
            dekompressor._reverseBWTransform(transforedData, 1, restoredData, 3)

    def test_reverseBWTransformBasic(self):
        """
        Purpose: Run a small input data set and ensure that it can be reversed
        Expectation: The reversed data should match the original data
        """

        kompressor = Kompressor(256, 0x00, 3, 0xFF, 4, 10)
        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        preTransformData = array('i', [1, 257, 2, 0, 4, 2, 5, 5, 5, 3, 4, 1, 2, 9, 0, 2, 1, 257]) # 18 bytes
        transforedData = array('i', [0]*19)
        restoredData = array('i', [0]*18)

        transformedLen = kompressor._performBWTransform(preTransformData, 18, transforedData, 19)
        self.assertEqual(19, transformedLen)

        restoreDataLen = dekompressor._reverseBWTransform(transforedData, 19, restoredData, 18)
        self.assertEqual(18, restoreDataLen)

        for i in range(0, 18):
            self.assertEqual(preTransformData[i], restoredData[i])

    def test_reverseBWTransform_Seq1(self):
        """
        Purpose: Test out a binary sequence
        Expectation: Data should come out the same as the original after reversal
        """

        kompressor = Kompressor(256, 0x00, 3, 0xFF, 4, 10)
        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        preTransformData = array('i',
                                 [0x56,0xba,0x71,0xd5,0x98,0x3b,0x5f,0x2f,
                                 0x56,0xba,0x71,0xd5,0x1c,0x00,0xa6,0x0e,
                                 0xb4,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                                 0x97,0x06,0xcb,0x00,0x00,0x00,0x68,0x11,
                                 0xb4,0x5e,0x4a,0x0e,0xe2,0x77,0xbf,0x1e,
                                 0xfa,0x3b,0x8d,0xbd,0x55,0x00,0xcb,0x03,
                                 0xc0,0xa7,0xb0,0xec,0x1c,0x00,0xa6,0x01,
                                 0x93,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                                 0x0a,0x07,0x8b,0x00,0x00,0x00,0x65,0x11,
                                 0x8c,0x5e,0x4a,0x0e,0xc6,0x7a,0xbe,0x1e,
                                 0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07]) #88
        transforedData = array('i', [0]*89)
        restoredData = array('i', [0]*88)

        transformedLen = kompressor._performBWTransform(preTransformData, 88, transforedData, 89)
        self.assertEqual(89, transformedLen)

        restoreDataLen = dekompressor._reverseBWTransform(transforedData, 89, restoredData, 88)
        self.assertEqual(88, restoreDataLen)

        for i in range(0, 88):
            self.assertEqual(preTransformData[i], restoredData[i])

    def test_reverseBWTransform_Seq2(self):
        """
        Purpose: Test a second sequence
        Expectation: Data should come out the same after reverse
        """

        kompressor = Kompressor(256, 0x00, 3, 0xFF, 4, 10)
        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        preTransformData = array('i',
                                 [0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03]) #160

        transforedData = array('i', [0]*161)
        restoredData = array('i', [0]*160)

        transformedLen = kompressor._performBWTransform(preTransformData, 160, transforedData, 161)
        self.assertEqual(161, transformedLen)

        restoreDataLen = dekompressor._reverseBWTransform(transforedData, 161, restoredData, 160)
        self.assertEqual(160, restoreDataLen)

        for i in range(0, 160):
            self.assertEqual(preTransformData[i], restoredData[i])

    def test_reverseBWTransform_Seq2_LargerDataSection(self):
        """
        Purpose: Test with sequence 2 but use a larger section size which will increase number of symbols used for transfor info to 2
        Expectation: Data should come out the same after reverse
        """

        kompressor = Kompressor(2048, 0x00, 3, 0xFF, 4, 10)
        dekompressor = Dekompressor(2048, 0x00, 3, 0xFF, 4, 10)

        preTransformData = array('i',
                                 [0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03]) #160

        transforedData = array('i', [0]*162)
        restoredData = array('i', [0]*160)

        transformedLen = kompressor._performBWTransform(preTransformData, 160, transforedData, 162)
        self.assertEqual(162, transformedLen)

        restoreDataLen = dekompressor._reverseBWTransform(transforedData, 162, restoredData, 160)
        self.assertEqual(160, restoreDataLen)

        for i in range(0, 160):
            self.assertEqual(preTransformData[i], restoredData[i])

    def test_reverseBWTransform_Seq3_LargerDataSection(self):
        """
        Purpose: Test with sequence 2 but use a larger section size which will increase number of symbols used for transfor info to 2
        Expectation: Data should come out the same after reverse
        """

        kompressor = Kompressor(2048, 0x00, 3, 0xFF, 4, 10)
        dekompressor = Dekompressor(2048, 0x00, 3, 0xFF, 4, 10)

        preTransformData = array('i',
                                 [
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03
                                 ]) #320

        transforedData = array('i', [0]*322)
        restoredData = array('i', [0]*320)

        transformedLen = kompressor._performBWTransform(preTransformData, 320, transforedData, 322)
        self.assertEqual(322, transformedLen)

        restoreDataLen = dekompressor._reverseBWTransform(transforedData, 322, restoredData, 320)
        self.assertEqual(320, restoreDataLen)

        for i in range(0, 320):
            self.assertEqual(preTransformData[i], restoredData[i])

    def test_reverseBWTransform_Seq4_LargerDataSection(self):
        """
        Purpose: Test with sequence 2 but use a larger section size which will increase number of symbols used for transfor info to 2
        Expectation: Data should come out the same after reverse
        """

        kompressor = Kompressor(2048, 0x00, 3, 0xFF, 4, 10)
        dekompressor = Dekompressor(2048, 0x00, 3, 0xFF, 4, 10)

        preTransformData = array('i', [1, 2, 258, 255, 255, 257, 3, 255, 3, 45, 255, 55, 55, 66, 99, 255, 255, 1, 2, 255, 0, 33, 255, 33, 33, 33, 33, 99, 255, 255, 255, 255, 255, 255])

        transforedData = array('i', [0]*36)
        restoredData = array('i', [0]*34)

        transformedLen = kompressor._performBWTransform(preTransformData, 34, transforedData, 36)
        self.assertEqual(36, transformedLen)

        restoreDataLen = dekompressor._reverseBWTransform(transforedData, 36, restoredData, 34)
        self.assertEqual(34, restoreDataLen)

        for i in range(0, 34):
            self.assertEqual(preTransformData[i], restoredData[i])

    def test_dekompressor_small_seq_allspecialsymbols(self):
        """
        Purpose: Kompressor and Dekompressor using a small data set and all special symbols
        Expectation: After undergoing compression and decompression the end data should be the same as the original
        """

        kompressor = Kompressor(2048, 0x00, 3, 0xFF, 4, 10)
        dekompressor = Dekompressor(2048, 0x00, 3, 0xFF, 4, 10)

        inputData = array('i', [1,2,0,0,0,0xFF,0,0,3,3,45,55,55,66,99,1,2,0,33,0xFF,33,33,33,33,99,0xFF,0xFF,0xFF]) #28
        inputDataToSend = array('i', [1,2,0,0,0,0xFF,0,0,3,3,45,55,55,66,99,1,2,0,33,0xFF,33,33,33,33,99,0xFF,0xFF,0xFF]) #28
        compressedData = bytearray(1024)
        testEncoder = SimpleEncoder(kompressor.mVocabularySize)
        kompressor.mEncoder = testEncoder

        self.assertEqual(28, len(inputDataToSend))
        compressedDataLen = kompressor.kompress(inputDataToSend, 28, compressedData, 1024)

        testDecoder = SimpleDecoder(testEncoder.mEncodedData, len(testEncoder.mEncodedData))
        dekompressor.mDecoder = testDecoder

        uncompressedData = bytearray(1024)
        uncompressedDataLen = dekompressor.dekompress(compressedData, compressedDataLen, uncompressedData, 1024)

        self.assertEqual(28, uncompressedDataLen)

        for i in range(0, 28):
            self.assertEqual(inputData[i], uncompressedData[i])

    def test_dekompressor_small_seq_2_allspecialsymbols(self):
        """
        Purpose: Kompressor and Dekompressor using a small data set and all special symbols
        Expectation: After undergoing compression and decompression the end data should be the same as the original
        """

        kompressor = Kompressor(2048, 0x00, 3, 0xFF, 4, 10)
        dekompressor = Dekompressor(2048, 0x00, 3, 0xFF, 4, 10)

        inputData = array('i', [1,2,0,0,0,0xFF,0xFF,0,0,3,0xFF,3,45,0xFF,55,55,66,99,0xFF,0xFF,1,2,0xFF,0,33,0xFF,33,33,33,33,99,0xFF,0xFF,0xFF]) #34
        inputDataToSend = array('i', [1,2,0,0,0,0xFF,0xFF,0,0,3,0xFF,3,45,0xFF,55,55,66,99,0xFF,0xFF,1,2,0xFF,0,33,0xFF,33,33,33,33,99,0xFF,0xFF,0xFF]) #34
        compressedData = bytearray(1024)
        testEncoder = SimpleEncoder(kompressor.mVocabularySize)
        kompressor.mEncoder = testEncoder

        self.assertEqual(34, len(inputDataToSend))
        compressedDataLen = kompressor.kompress(inputDataToSend, 34, compressedData, 1024)

        testDecoder = SimpleDecoder(testEncoder.mEncodedData, len(testEncoder.mEncodedData))
        dekompressor.mDecoder = testDecoder

        uncompressedData = bytearray(1024)
        uncompressedDataLen = dekompressor.dekompress(compressedData, compressedDataLen, uncompressedData, 1024)

        self.assertEqual(34, uncompressedDataLen)

        for i in range(0, 34):
            self.assertEqual(inputData[i], uncompressedData[i])

    def test_dekompressor_small_seq_only_specialsymbol1(self):
        """
        Purpose: Kompressor and Dekompressor using a small data set and only special symbol 1
        Expectation: After undergoing compression and decompression the end data should be the same as the original
        """

        kompressor = Kompressor(2048, 0x00, 3, 0xFF, 0, 10)
        dekompressor = Dekompressor(2048, 0x00, 3, 0xFF, 0, 10)

        inputData = array('i', [1,2,0,0,0,0xFF,0xFF,0,0,3,0xFF,3,45,0xFF,55,55,66,99,0xFF,0xFF,1,2,0xFF,0,33,0xFF,33,33,33,33,99,0xFF,0xFF,0xFF]) #34
        inputDataToSend = array('i', [1,2,0,0,0,0xFF,0xFF,0,0,3,0xFF,3,45,0xFF,55,55,66,99,0xFF,0xFF,1,2,0xFF,0,33,0xFF,33,33,33,33,99,0xFF,0xFF,0xFF]) #34

        compressedData = bytearray(1024)
        testEncoder = SimpleEncoder(kompressor.mVocabularySize)
        kompressor.mEncoder = testEncoder

        self.assertEqual(34, len(inputDataToSend))
        compressedDataLen = kompressor.kompress(inputDataToSend, 34, compressedData, 1024)

        testDecoder = SimpleDecoder(testEncoder.mEncodedData, len(testEncoder.mEncodedData))
        dekompressor.mDecoder = testDecoder

        uncompressedData = bytearray(1024)
        uncompressedDataLen = dekompressor.dekompress(compressedData, compressedDataLen, uncompressedData, 1024)

        self.assertEqual(34, uncompressedDataLen)

        for i in range(0, 34):
            self.assertEqual(inputData[i], uncompressedData[i])

    def test_dekompressor_small_seq_only_specialsymbol2(self):
        """
        Purpose: Kompressor and Dekompressor using a small data set and only special symbol 2
        Expectation: After undergoing compression and decompression the end data should be the same as the original
        """

        kompressor = Kompressor(2048, 0x00, 0, 0xFF, 3, 10)
        dekompressor = Dekompressor(2048, 0x00, 0, 0xFF, 3, 10)

        inputData = array('i', [1,2,0,0,0,0xFF,0xFF,0,0,3,0xFF,3,45,0xFF,55,55,66,99,0xFF,0xFF,1,2,0xFF,0,33,0xFF,33,33,33,33,99,0xFF,0xFF,0xFF]) #34
        inputDataToSend = array('i', [1,2,0,0,0,0xFF,0xFF,0,0,3,0xFF,3,45,0xFF,55,55,66,99,0xFF,0xFF,1,2,0xFF,0,33,0xFF,33,33,33,33,99,0xFF,0xFF,0xFF]) #34

        compressedData = bytearray(1024)
        testEncoder = SimpleEncoder(kompressor.mVocabularySize)
        kompressor.mEncoder = testEncoder

        self.assertEqual(34, len(inputDataToSend))
        compressedDataLen = kompressor.kompress(inputDataToSend, 34, compressedData, 1024)

        testDecoder = SimpleDecoder(testEncoder.mEncodedData, len(testEncoder.mEncodedData))
        dekompressor.mDecoder = testDecoder

        uncompressedData = bytearray(1024)
        uncompressedDataLen = dekompressor.dekompress(compressedData, compressedDataLen, uncompressedData, 1024)

        self.assertEqual(34, uncompressedDataLen)

        for i in range(0, 34):
            self.assertEqual(inputData[i], uncompressedData[i])

    def test_dekompressor_larger_seq_testdecoder(self):
        """
        Purpose: Kompressor and Dekompressor using a larger data set using test decoder
        Expectation: After undergoing compression and decompression the end data should be the same as the original
        """

        kompressor = Kompressor(2048, 0x00, 0, 0xFF, 3, 10)
        dekompressor = Dekompressor(2048, 0x00, 0, 0xFF, 3, 10)

        inputData = array('i',
                                 [
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03
                                 ]) #320

        inputDataToSend = array('i',
                                 [
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03
                                 ]) #320

        compressedData = bytearray(1024)
        testEncoder = SimpleEncoder(kompressor.mVocabularySize)
        kompressor.mEncoder = testEncoder

        self.assertEqual(320, len(inputDataToSend))
        compressedDataLen = kompressor.kompress(inputDataToSend, 320, compressedData, 1024)

        testDecoder = SimpleDecoder(testEncoder.mEncodedData, len(testEncoder.mEncodedData))
        dekompressor.mDecoder = testDecoder

        uncompressedData = bytearray(1024)
        uncompressedDataLen = dekompressor.dekompress(compressedData, compressedDataLen, uncompressedData, 1024)

        self.assertEqual(320, uncompressedDataLen)

        for i in range(0, 320):
            self.assertEqual(inputData[i], uncompressedData[i])

    def test_dekompressor_larger_seq_realdecoder(self):
        """
        Purpose: Kompressor and Dekompressor using a larger data set
        Expectation: After undergoing compression and decompression the end data should be the same as the original
        """

        kompressor = Kompressor(2048, 0x00, 0, 0xFF, 3, 10)
        dekompressor = Dekompressor(2048, 0x00, 0, 0xFF, 3, 10)

        inputData = array('i',
                                 [
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03
                                 ]) #320

        inputDataToSend = array('i',
                                 [
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03
                                 ]) #320

        inputDataLen = len(inputDataToSend)

        compressedData = bytearray(1024)

        compressedDataLen = kompressor.kompress(inputDataToSend, inputDataLen, compressedData, 1024)

        uncompressedData = bytearray(1024)
        uncompressedDataLen = dekompressor.dekompress(compressedData, compressedDataLen, uncompressedData, 1024)

        self.assertEqual(inputDataLen, uncompressedDataLen)

        for i in range(0, inputDataLen):
            self.assertEqual(inputData[i], uncompressedData[i])

    def test_dekompressor_larger_seq_realdecoder_multiblock(self):
        """
        Purpose: Kompressor and Dekompressor using a larger data compressed several times
        Expectation: After undergoing compression and decompression the end data should be the same as the original
        """

        kompressor = Kompressor(2048, 0x00, 0, 0xFF, 3, 10)
        dekompressor = Dekompressor(2048, 0x00, 0, 0xFF, 3, 10)

        inputData = array('i',
                                 [
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                                 0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                 0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                 0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                 0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                 0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                 0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                 0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                 0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                 0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03
                                 ]) #320

        inputDataToSend = array('i', inputData)
        inputDataToSend2 = array('i', inputData)
        inputDataToSend3 = array('i', inputData)

        inputDataLen = len(inputDataToSend)

        compressedData = bytearray(1024)

        compressedDataLen = kompressor.kompress(inputDataToSend, inputDataLen, compressedData, 1024,lastDataBlock=False)

        uncompressedData = bytearray(1024)
        uncompressedDataLen = dekompressor.dekompress(compressedData, compressedDataLen, uncompressedData, 1024)

        self.assertEqual(inputDataLen, uncompressedDataLen)

        for i in range(0, inputDataLen):
            self.assertEqual(inputData[i], uncompressedData[i])

        compressedDataLen = kompressor.kompress(inputDataToSend2, inputDataLen, compressedData, 1024,lastDataBlock=False)

        uncompressedData = bytearray(1024)
        uncompressedDataLen = dekompressor.dekompress(compressedData, compressedDataLen, uncompressedData, 1024)

        self.assertEqual(inputDataLen, uncompressedDataLen)

        for i in range(0, inputDataLen):
            self.assertEqual(inputData[i], uncompressedData[i])

        compressedDataLen = kompressor.kompress(inputDataToSend3, inputDataLen, compressedData, 1024,lastDataBlock=False)

        uncompressedData = bytearray(1024)
        uncompressedDataLen = dekompressor.dekompress(compressedData, compressedDataLen, uncompressedData, 1024)

        self.assertEqual(inputDataLen, uncompressedDataLen)

        for i in range(0, inputDataLen):
            self.assertEqual(inputData[i], uncompressedData[i])


    def test_dekompressor_largefile(self):
        """
        Purpose: Read in a hex file in ascii format line by line, convert to binary and compress and decompress
        Expectation: Decompressed data should match compressed data
        """

        kompressor = Kompressor(2048, 0x00, 5, 0x00, 0, 15)
        dekompressor = Dekompressor(2048, 0x00, 5, 0x00, 0, 15)

        testFile = 'testFile.ascii'

        inputData = array('i', [0]*2048)
        compressedData = bytearray(2048)
        decompressedData = bytearray(2048)
        count = 0

        with open(testFile, 'r+') as f:

            for line in f:

                # Strip terminating characters and conver to hex from ascii
                line = line.strip()
                lineBytes = bytearray.fromhex(line)
                inputDataSize = len(lineBytes)

                # Copy the data into the integer array
                for i in range(0, inputDataSize):
                    inputData[i] = lineBytes[i]

                if(count == 47):
                    x = 2

                compressedLineLen = kompressor.kompress(inputData, inputDataSize, compressedData, 2048, lastDataBlock=False)

                decompressedLineLen = dekompressor.dekompress(compressedData, compressedLineLen, decompressedData, 2048)

                self.assertEqual(decompressedLineLen, inputDataSize)
                self.assertEqual(decompressedData[:decompressedLineLen],lineBytes)

                count += 1


if __name__ == '__main__':
    unittest.main()
