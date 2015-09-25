__author__ = 'marko'

import unittest
from AREncoder import AREncoder
from ARDecoder import ARDecoder
from array import array

class TestARDecoder(unittest.TestCase):

    def test_instantiate_ARDecoder_invalid_parameters(self):
        # Purpose: Instantiate object with invalid word size parameter
        # Expectation: An exception should be thrown

        with self.assertRaises(Exception):
            ARDecoder(0, 256, 256)

    def test_instantiate_ARDecoder_valid(self):
        # Purpose: Instantiate ARDecoder with valid parameters
        # Expectation: The member variables should be initialized correctly

        test_ardecoder = ARDecoder(11, 256, 256)

        self.assertEqual(512, test_ardecoder.mMaxDecodingBytes)
        self.assertEqual(256, test_ardecoder.mVocabularySize)
        self.assertEqual(256, test_ardecoder.mTerminationSymbol)
        self.assertEqual(11, test_ardecoder.mWordSize)
        self.assertEqual(0x07FF, test_ardecoder.mWordBitMask)
        self.assertEqual(0x0400, test_ardecoder.mWordMSBMask)
        self.assertEqual(0x0200, test_ardecoder.mWordSecondMSBMask)
        self.assertNotEqual(None, test_ardecoder.mSymbolCount)
        self.assertEqual(None, test_ardecoder.mEncodedData)
        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(None, test_ardecoder.mDecodedData)
        self.assertEqual(0, test_ardecoder.mDecodedDataLen)

        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataByteIndex)
        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataBit)
        self.assertEqual(256, test_ardecoder.mTotalSymbolCount)

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(test_ardecoder.mWordBitMask, test_ardecoder.mUpperTag)
        self.assertEqual(0, test_ardecoder.mCurrentTag)

    def test_reset(self):
        # Purpose: Re-initialize the members
        # Expectation: Ensure that data is initialized properly

        test_ardecoder = ARDecoder(11, 256, 256)

        test_ardecoder.mTotalSymbolCount = 49
        test_ardecoder.mCompressedDataCount = 33
        test_ardecoder.mLowerTag = 7
        test_ardecoder.mUpperTag = 9
        test_ardecoder.mCurrentTag = 99
        test_ardecoder.mCurrentByte = 0xFF
        test_ardecoder.mCurrentBitCount = 9
        test_ardecoder.mCompressedData = 1
        test_ardecoder.mCompressedDataCount = 99
        test_ardecoder.mCurrentEncodedByteIndex = 44
        test_ardecoder.mCurrentEncodedDataBit = 99
        test_ardecoder.mEncodedData = bytearray()
        test_ardecoder.mDecodedData = bytearray()

        # Initialize byte array to a count of one for each symbol
        for i in range(0, test_ardecoder.mVocabularySize):
            test_ardecoder.mSymbolCount[i] = 4

        test_ardecoder.reset();

        self.assertEqual(512, test_ardecoder.mMaxDecodingBytes)
        self.assertEqual(11, test_ardecoder.mWordSize)
        self.assertEqual(0x07FF, test_ardecoder.mWordBitMask)
        self.assertEqual(0x0400, test_ardecoder.mWordMSBMask)
        self.assertEqual(0x0200, test_ardecoder.mWordSecondMSBMask)
        self.assertNotEqual(None, test_ardecoder.mSymbolCount)
        self.assertEqual(None, test_ardecoder.mEncodedData)
        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(None, test_ardecoder.mDecodedData)
        self.assertEqual(0, test_ardecoder.mDecodedDataLen)

        self.assertEqual(test_ardecoder.mVocabularySize, test_ardecoder.mTotalSymbolCount)
        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataByteIndex)
        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataBit)

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(test_ardecoder.mWordBitMask, test_ardecoder.mUpperTag)
        self.assertEqual(0, test_ardecoder.mCurrentTag)

        # Ensure that the cumulative count is initialized properly
        for i in range(0, test_ardecoder.mVocabularySize):
            self.assertEqual(1, test_ardecoder.mSymbolCount[i])

    def test_get_next_bit_exceedmax(self):
        # Purpose: Attempt to get the next bit when we have gone through all the encoded data
        # Expectation: An exception should be raised

        test_ardecoder = ARDecoder(11, 256, 256)

        test_ardecoder.mCurrentEncodedDataByteIndex = 10
        test_ardecoder.mEncodedDataCount = 10

        with self.assertRaises(Exception):
            test_ardecoder._get_next_bit()


    def test_get_next_bit_valid_Data(self):
        # Purpose: Get several bits of upcoming
        # Expectation: The correct bits should be returned

        test_ardecoder = ARDecoder(11, 256, 256)

        test_ardecoder.reset()

        test_ardecoder.mCurrentEncodedDataByteIndex = 0
        test_ardecoder.mEncodedDataCount = 10
        test_ardecoder.mEncodedData = bytearray(10)

        test_ardecoder.mEncodedData[0] = 0xAA
        test_ardecoder.mEncodedData[1] = 0xBB
        test_ardecoder.mEncodedData[2] = 0xFF
        test_ardecoder.mEncodedData[3] = 0x00


        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder.mCurrentEncodedDataBit)
        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(2, test_ardecoder.mCurrentEncodedDataBit)
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(3, test_ardecoder.mCurrentEncodedDataBit)
        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(4, test_ardecoder.mCurrentEncodedDataBit)
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(5, test_ardecoder.mCurrentEncodedDataBit)
        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(6, test_ardecoder.mCurrentEncodedDataBit)
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(7, test_ardecoder.mCurrentEncodedDataBit)
        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataBit)

        self.assertEqual(1, test_ardecoder.mCurrentEncodedDataByteIndex)

        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder._get_next_bit())

        self.assertEqual(2, test_ardecoder.mCurrentEncodedDataByteIndex)
        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataBit)

        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder._get_next_bit())
        self.assertEqual(1, test_ardecoder._get_next_bit())

        self.assertEqual(3, test_ardecoder.mCurrentEncodedDataByteIndex)
        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataBit)

        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(0, test_ardecoder._get_next_bit())
        self.assertEqual(0, test_ardecoder._get_next_bit())

        self.assertEqual(4, test_ardecoder.mCurrentEncodedDataByteIndex)
        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataBit)

    def test_increment_count(self):
        # Purpose: Increment various indexes
        # Expectation: The cumulative counts will be updated appropriately

        test_ardecoder = ARDecoder(11, 256, 256)

        for i in range(0, test_ardecoder.mVocabularySize):
            self.assertEqual(1, test_ardecoder.mSymbolCount[i])

        self.assertEqual(1, test_ardecoder.mSymbolCount[255])
        self.assertEqual(256, test_ardecoder.mTotalSymbolCount)

        test_ardecoder._increment_count(0)
        self.assertEqual(257, test_ardecoder.mTotalSymbolCount)

        test_ardecoder._increment_count(50)
        self.assertEqual(258, test_ardecoder.mTotalSymbolCount)

        test_ardecoder._increment_count(50)
        self.assertEqual(259, test_ardecoder.mTotalSymbolCount)

        self.assertEqual(1, test_ardecoder.mSymbolCount[255])

        test_ardecoder._increment_count(255)
        self.assertEqual(260, test_ardecoder.mTotalSymbolCount)

        self.assertEqual(2, test_ardecoder.mSymbolCount[255])

    def test_increment_count_pastmax(self):
        # Purpose: Increment various indexes until we surpass the max bytes
        # Expectation: The stats should be normalized

        test_ardecoder = ARDecoder(11, 256, 256)

        for i in range(0, test_ardecoder.mVocabularySize):
            self.assertEqual(1, test_ardecoder.mSymbolCount[i])

        for i in range(0, 100):
            test_ardecoder._increment_count(0)

        for i in range(0, 100):
            test_ardecoder._increment_count(200)

        self.assertEqual(456, test_ardecoder.mTotalSymbolCount)

        for i in range(0, 55):
            test_ardecoder._increment_count(255)

        self.assertEqual(511, test_ardecoder.mTotalSymbolCount)

        test_ardecoder._increment_count(255)

        # Normalization should occur now
        self.assertEqual(50, test_ardecoder.mSymbolCount[0])
        self.assertEqual(50, test_ardecoder.mSymbolCount[200])
        self.assertEqual(28, test_ardecoder.mSymbolCount[255])

        self.assertEqual(381, test_ardecoder.mTotalSymbolCount)

    def test_normalize_stats(self):
        # Purpose: Normalize statistics across several ranges
        # Expectation: The cumulative counts should be correct after each normalization

        test_ardecoder = ARDecoder(11, 256, 256)

        # Normalize unchanged data, it should remain the same
        test_ardecoder._normalize_stats();

        self.assertEqual(256, test_ardecoder.mTotalSymbolCount)

        self.assertEqual(1, test_ardecoder.mSymbolCount[0])
        self.assertEqual(1, test_ardecoder.mSymbolCount[1])
        self.assertEqual(1, test_ardecoder.mSymbolCount[64])
        self.assertEqual(1, test_ardecoder.mSymbolCount[250])
        self.assertEqual(1, test_ardecoder.mSymbolCount[255])


        for i in range(0, test_ardecoder.mVocabularySize):
            self.assertEqual(1, test_ardecoder.mSymbolCount[i])

        # Normalize changed data, All count should be halved
        for i in range(0,10):
            test_ardecoder._increment_count(0)

        for i in range(0,10):
            test_ardecoder._increment_count(250)

        for i in range(0,10):
            test_ardecoder._increment_count(255)

        self.assertEqual(286, test_ardecoder.mTotalSymbolCount)

        test_ardecoder._normalize_stats();

        self.assertEqual(268, test_ardecoder.mTotalSymbolCount)

        self.assertEqual(5, test_ardecoder.mSymbolCount[0])
        self.assertEqual(1, test_ardecoder.mSymbolCount[1])
        self.assertEqual(1, test_ardecoder.mSymbolCount[64])
        self.assertEqual(5, test_ardecoder.mSymbolCount[250])
        self.assertEqual(5, test_ardecoder.mSymbolCount[255])

    def test_rescale_none_required(self):
        # Purpose: Call when the lower and upper tag are in a range that requires no rescaling
        # Expectation: The tags should not be modified and no bits should be added to compressed data

        test_ardecoder = ARDecoder(11, 256, 256)

        test_ardecoder.mLowerTag = 510    # b00111111110 (just below quarter mark)
        test_ardecoder.mUpperTag = 1025   # b10000000001 (halfway point)
        test_ardecoder.mCurrentTag = 700

        test_ardecoder.mEncodedData = bytearray(10)
        test_ardecoder.mEncodedData[0] = 0xFF
        test_ardecoder.mEncodedDataCount  = 1

        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataByteIndex)
        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataBit)

        test_ardecoder._rescale()

        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataByteIndex)
        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataBit)

        self.assertEqual(510, test_ardecoder.mLowerTag)
        self.assertEqual(1025, test_ardecoder.mUpperTag)
        self.assertEqual(700, test_ardecoder.mCurrentTag)

    def test_rescale_E1_required(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E1 scaling
        # Expectation: The tags should be modified according to E1 and a 0 bit should be added to compressed data

        test_ardecoder = ARDecoder(11, 256, 256)

        test_ardecoder.reset()

        test_ardecoder.mEncodedData = bytearray(10)
        test_ardecoder.mEncodedData[0] = 0xFF
        test_ardecoder.mEncodedDataCount = 1

        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataByteIndex)
        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataBit)

        test_ardecoder.mLowerTag = 0          # bottom of range
        test_ardecoder.mUpperTag = 1000       # just below middle of range
        test_ardecoder.mCurrentTag = 500

        test_ardecoder._rescale()

        self.assertEqual(0, test_ardecoder.mCurrentEncodedDataByteIndex)
        self.assertEqual(1, test_ardecoder.mCurrentEncodedDataBit)

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(2001, test_ardecoder.mUpperTag)
        self.assertEqual(1001, test_ardecoder.mCurrentTag)

    """
    def test_rescale_E1_required_with_E3ScaleCount(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E1 scaling and there is a count of 2 on the E3 Scale Count
        # Expectation: The tags should be modified according to E1 and a 0 bit should be added to compressed data. Two 0 bits should be added to compensate for E3 Scale Count

        test_ardecoder = ARDecoder(11, 256, 256)

        test_ardecoder.mEncodedData = bytearray(10)

        test_ardecoder.mLowerTag = 0      # b00000000000 (0)
        test_ardecoder.mUpperTag = 1022   # b01111111110 (just below halfway point)

        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(0, test_ardecoder.mEncodedData[0])

        test_ardecoder.mE3ScaleCount = 2

        test_ardecoder._rescale()

        self.assertEqual(0, test_ardecoder.mE3ScaleCount)
        self.assertEqual(3, test_ardecoder.mCurrentBitCount)
        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(3, test_ardecoder.mEncodedData[0])

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(2045, test_ardecoder.mUpperTag)

    def test_rescale_E1_requiredmultiple(self):
        # Purpose: Call when the lower and upper tag are in a range that requires multiple E1 scalings
        # Expectation: The tags should be modified according to E1 and a 0 bit should be added to compressed data as many times as E1 was performed

        test_ardecoder = ARDecoder(11, 256, 256)
        test_ardecoder.mEncodedData = bytearray(10)

        test_ardecoder.mLowerTag = 0    # b00000000000
        test_ardecoder.mUpperTag = 256  # b00100000000

        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(0, test_ardecoder.mEncodedData[0])

        test_ardecoder._rescale()

        self.assertEqual(2, test_ardecoder.mCurrentBitCount)
        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(0, test_ardecoder.mEncodedData[0])

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(1027, test_ardecoder.mUpperTag)

    def test_rescale_E2_required(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E2 scaling
        # Expectation: The tags should be modified according to E2 and a 1 bit should be added to compressed data

        test_ardecoder = ARDecoder(11, 256, 256)

        test_ardecoder.mEncodedData = bytearray(10)

        test_ardecoder.mLowerTag = 1024   # b10000000000 (above halfway)
        test_ardecoder.mUpperTag = 2012   # b11111011100

        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(0, test_ardecoder.mEncodedData[0])

        test_ardecoder._rescale()

        self.assertEqual(1, test_ardecoder.mCurrentBitCount)
        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(1, test_ardecoder.mEncodedData[0])

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(1977, test_ardecoder.mUpperTag)

    def test_rescale_E2_required_with_E3ScaleCount(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E2 scaling and there is a count of 2 on the E3 Scale Count
        # Expectation: The tags should be modified according to E2 and a 1 bit should be added to compressed data. Two 0 bits should be added to compensate for E3 Scale Count

        test_ardecoder = ARDecoder(11, 256, 256)

        test_ardecoder.mEncodedData = bytearray(10)

        test_ardecoder.mLowerTag = 1024   # b10000000000 (above halfway)
        test_ardecoder.mUpperTag = 2012   # b11111011100

        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(0, test_ardecoder.mEncodedData[0])

        test_ardecoder.mE3ScaleCount = 2

        test_ardecoder._rescale()

        self.assertEqual(0, test_ardecoder.mE3ScaleCount)
        self.assertEqual(3, test_ardecoder.mCurrentBitCount)
        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(0x4, test_ardecoder.mEncodedData[0])

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(1977, test_ardecoder.mUpperTag)

    def test_rescale_E2_requiredmultiple(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E2 scaling multiple times
        # Expectation: The tags should be modified according to E2 and a 1 bit should be added to compressed data for each scaling

        test_ardecoder = ARDecoder(11, 256, 256)

        test_ardecoder.mEncodedData = bytearray(10)

        test_ardecoder.mLowerTag = 1536   # b11000000000
        test_ardecoder.mUpperTag = 2047   # b11111111111

        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(0, test_ardecoder.mEncodedData[0])

        test_ardecoder._rescale()

        self.assertEqual(2, test_ardecoder.mCurrentBitCount)
        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(0x3, test_ardecoder.mEncodedData[0])

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(2047, test_ardecoder.mUpperTag)

    def test_rescale_E3_required(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E3 scaling
        # Expectation: The tags should be modified according to E3 and the E3 scale count should be incremented

        test_ardecoder = ARDecoder(11, 256, 256)

        test_ardecoder.mLowerTag = 512    # b01000000000 (above quarter mark)
        test_ardecoder.mUpperTag = 1500   # b10111011100 (below 3 quarters mark

        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(0, test_ardecoder.mEncodedData[0])

        test_ardecoder._rescale()

        self.assertEqual(0, test_ardecoder.mCurrentBitCount)
        self.assertEqual(1, test_ardecoder.mE3ScaleCount)
        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(0, test_ardecoder.mEncodedData[0])

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(1976, test_ardecoder.mUpperTag)

    def test_rescale_E3multiple(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E3 scaling multiple times
        # Expectation: The tags should be modified by E3

        test_ardecoder = ARDecoder(11, 256, 256)

        test_ardecoder.mLowerTag = 812    # b01100101100
        test_ardecoder.mUpperTag = 1162   # b10010001010

        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(0, test_ardecoder.mEncodedData[0])

        test_ardecoder._rescale()

        self.assertEqual(0, test_ardecoder.mCurrentBitCount)
        self.assertEqual(2, test_ardecoder.mE3ScaleCount)
        self.assertEqual(0, test_ardecoder.mEncodedDataCount)
        self.assertEqual(0, test_ardecoder.mEncodedData[0])

        self.assertEqual(176, test_ardecoder.mLowerTag)
        self.assertEqual(1576, test_ardecoder.mUpperTag)

    def test_update_range_tags(self):
        # Purpose: Test updating the upper lower tags with incoming symbols
        # Expectation: The upper and lower tags should be updated correctly and the stat counts should be incremented appropriately

        test_ardecoder = ARDecoder(11, 256, 256)

        test_ardecoder.mLowerTag = 0
        test_ardecoder.mUpperTag = 2047

        # Pass in index for symbol 0x00 which currently has cumulative count of 1 out of total count of 256
        test_ardecoder._update_range_tags(0)

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(7, test_ardecoder.mUpperTag)

        self.assertEqual(2, test_ardecoder.mSymbolCount[0])
        self.assertEqual(257, test_ardecoder.mTotalSymbolCount)
        self.assertEqual(0, test_ardecoder.mEncodedDataCount)

        # _rescale
        test_ardecoder._rescale();

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(2047, test_ardecoder.mUpperTag)

        self.assertEqual(2, test_ardecoder.mSymbolCount[0])
        self.assertEqual(257, test_ardecoder.mTotalSymbolCount)

        # Pass in index for symbol 0x00 which currently has cumulative count of 2 out of total count of 257
        test_ardecoder._update_range_tags(0)

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(14, test_ardecoder.mUpperTag)

        self.assertEqual(3, test_ardecoder.mSymbolCount[0])
        self.assertEqual(258, test_ardecoder.mTotalSymbolCount)

        # _rescale
        test_ardecoder._rescale();

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(1919, test_ardecoder.mUpperTag)

        self.assertEqual(3, test_ardecoder.mSymbolCount[0])
        self.assertEqual(258, test_ardecoder.mTotalSymbolCount)

        # Pass in index for symbol 0xAA which currently has cumulative count of count out of 173 total count of 258
        self.assertEqual(172, test_ardecoder.mSymbolCount[0xA9])
        self.assertEqual(173, test_ardecoder.mSymbolCount[0xAA])
        test_ardecoder._update_range_tags(0xAA)

        self.assertEqual(1280, test_ardecoder.mLowerTag)
        self.assertEqual(1286, test_ardecoder.mUpperTag)

        self.assertEqual(3, test_ardecoder.mSymbolCount[0])
        self.assertEqual(172, test_ardecoder.mSymbolCount[0xA9])
        self.assertEqual(174, test_ardecoder.mSymbolCount[0xAA])
        self.assertEqual(259, test_ardecoder.mTotalSymbolCount)

        # _rescale
        test_ardecoder._rescale();

        self.assertEqual(0, test_ardecoder.mLowerTag)
        self.assertEqual(1791, test_ardecoder.mUpperTag)

        self.assertEqual(3, test_ardecoder.mSymbolCount[0])
        self.assertEqual(172, test_ardecoder.mSymbolCount[0xA9])
        self.assertEqual(174, test_ardecoder.mSymbolCount[0xAA])
        self.assertEqual(259, test_ardecoder.mTotalSymbolCount)

        self.assertEqual(2, test_ardecoder.mEncodedDataCount)

    """
    def test_decode_data_small_set(self):
        # Purpose: Encoded the data set {0x00, 0x00, 0x01}
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(11, 257)
        test_ardecoder = ARDecoder(11, 257, 256)

        data = array('i', [0]*16)
        encodedData = bytearray(16)
        decodedData = bytearray(16)
        encodedDataSize = 0
        decodedDataSize = 0

        data[0] = 0x00
        data[1] = 0x00
        data[2] = 0x01
        data[3] = 256

        encodedDataSize = test_arencoder.encode(data, 4, encodedData, 16)

        self.assertEqual(6, encodedDataSize)
        self.assertEqual(0x00, encodedData[0])
        self.assertEqual(0x00, encodedData[1])
        self.assertEqual(0x06, encodedData[2])
        self.assertEqual(62, encodedData[3])
        self.assertEqual(128, encodedData[4])
        self.assertEqual(0, encodedData[5])

        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,16)

        self.assertEqual(decodedDataSize, 3)
        self.assertEqual(decodedData[0], 0x00)
        self.assertEqual(decodedData[1], 0x00)
        self.assertEqual(decodedData[2], 0x01)

    def test_encode_decode_data_small_set2(self):
        # Purpose: Encode the data set {0x00, 0x00, 0x01, 0x01}
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(11, 257)
        test_ardecoder = ARDecoder(11, 257, 256)

        data = array('i', [0]*10)
        encodedData = bytearray(10)
        decodedData = bytearray(16)
        encodedDataSize = 0
        decodedDataSize = 0

        data[0] = 0x00
        data[1] = 0x00
        data[2] = 0x01
        data[3] = 0x01
        data[4] = 256

        encodedDataSize = test_arencoder.encode(data, 5, encodedData, 10)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,16)

        self.assertEqual(decodedDataSize, 4)

        for i in range(0,4):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_multiple_blocks(self):
        # Purpose: Encode several blocks and then decode them
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(11, 257)
        test_ardecoder = ARDecoder(11, 257, 256)

        data = array('i',
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
                     0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07,256]) # 89

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        decodedData2 = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024, lastDataBlock=False)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024, lastDataBlock=False)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData2,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData2[i])

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData2,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData2[i])

    def test_encode_decode_data_larger_set1(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(11, 257)
        test_ardecoder = ARDecoder(11, 257, 256)

        data = array('i',
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
                     0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07,256]) # 89

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set2(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(11, 257)
        test_ardecoder = ARDecoder(11, 257, 256)

        data = array('i',
                     [0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                     0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                     0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                     0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set3(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(11, 257)
        test_ardecoder = ARDecoder(11, 257, 256)

        data = array('i',
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
                     0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set4(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(11, 257)
        test_ardecoder = ARDecoder(11, 257, 256)

        data = array('i',
                     [0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                     0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                     0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                     0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,
                     0x56,0xba,0x71,0xd5,0x98,0x3b,0x5f,0x2f,
                     0x56,0xba,0x71,0xd5,0x1c,0x00,0xa6,0x0e,
                     0xb4,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                     0x97,0x06,0xcb,0x00,0x00,0x00,0x68,0x11,
                     0xb4,0x5e,0x4a,0x0e,0xe2,0x77,0xbf,0x1e,
                     0xfa,0x3b,0x8d,0xbd,0x55,0x00,0xcb,0x03,
                     0xc0,0xa7,0xb0,0xec,0x1c,0x00,0xa6,0x01,
                     0x93,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                     0x0a,0x07,0x8b,0x00,0x00,0x00,0x65,0x11,
                     0x8c,0x5e,0x4a,0x0e,0xc6,0x7a,0xbe,0x1e,
                     0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07,
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
                     0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set1_12bit(self):
        # Purpose: Encode a large data set using 12 bit word size
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(12, 257)
        test_ardecoder = ARDecoder(12, 257, 256)

        data = array('i',
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
                     0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07,256]) # 89

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set2_12bit(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(12, 257)
        test_ardecoder = ARDecoder(12, 257, 256)

        data = array('i',
                     [0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                     0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                     0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                     0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set3_12bit(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(12, 257)
        test_ardecoder = ARDecoder(12, 257, 256)

        data = array('i',
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
                     0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set4_12bit(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(12, 257)
        test_ardecoder = ARDecoder(12, 257, 256)

        data = array('i',
                     [0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                     0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                     0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                     0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,
                     0x56,0xba,0x71,0xd5,0x98,0x3b,0x5f,0x2f,
                     0x56,0xba,0x71,0xd5,0x1c,0x00,0xa6,0x0e,
                     0xb4,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                     0x97,0x06,0xcb,0x00,0x00,0x00,0x68,0x11,
                     0xb4,0x5e,0x4a,0x0e,0xe2,0x77,0xbf,0x1e,
                     0xfa,0x3b,0x8d,0xbd,0x55,0x00,0xcb,0x03,
                     0xc0,0xa7,0xb0,0xec,0x1c,0x00,0xa6,0x01,
                     0x93,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                     0x0a,0x07,0x8b,0x00,0x00,0x00,0x65,0x11,
                     0x8c,0x5e,0x4a,0x0e,0xc6,0x7a,0xbe,0x1e,
                     0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07,
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
                     0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set1_16bit(self):
        # Purpose: Encode a large data set using 16 bit word size
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(16, 257)
        test_ardecoder = ARDecoder(16, 257, 256)

        data = array('i',
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
                     0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07,256]) # 89

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set2_16bit(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(16, 257)
        test_ardecoder = ARDecoder(16, 257, 256)

        data = array('i',
                     [0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                     0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                     0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                     0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set3_16bit(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(16, 257)
        test_ardecoder = ARDecoder(16, 257, 256)

        data = array('i',
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
                     0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set4_16bit(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(16, 257)
        test_ardecoder = ARDecoder(16, 257, 256)

        data = array('i',
                     [0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                     0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                     0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                     0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,
                     0x56,0xba,0x71,0xd5,0x98,0x3b,0x5f,0x2f,
                     0x56,0xba,0x71,0xd5,0x1c,0x00,0xa6,0x0e,
                     0xb4,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                     0x97,0x06,0xcb,0x00,0x00,0x00,0x68,0x11,
                     0xb4,0x5e,0x4a,0x0e,0xe2,0x77,0xbf,0x1e,
                     0xfa,0x3b,0x8d,0xbd,0x55,0x00,0xcb,0x03,
                     0xc0,0xa7,0xb0,0xec,0x1c,0x00,0xa6,0x01,
                     0x93,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                     0x0a,0x07,0x8b,0x00,0x00,0x00,0x65,0x11,
                     0x8c,0x5e,0x4a,0x0e,0xc6,0x7a,0xbe,0x1e,
                     0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07,
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
                     0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set1_32bit(self):
        # Purpose: Encode a large data set using 16 bit word size
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(16, 257)
        test_ardecoder = ARDecoder(16, 257, 256)

        data = array('i',
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
                     0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07,256]) # 89

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set2_32bit(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(16, 257)
        test_ardecoder = ARDecoder(16, 257, 256)

        data = array('i',
                     [0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                     0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                     0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                     0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set3_32bit(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(16, 257)
        test_ardecoder = ARDecoder(16, 257, 256)

        data = array('i',
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
                     0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set4_32bit(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(16, 257)
        test_ardecoder = ARDecoder(16, 257, 256)

        data = array('i',
                     [0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                     0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                     0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                     0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,
                     0x56,0xba,0x71,0xd5,0x98,0x3b,0x5f,0x2f,
                     0x56,0xba,0x71,0xd5,0x1c,0x00,0xa6,0x0e,
                     0xb4,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                     0x97,0x06,0xcb,0x00,0x00,0x00,0x68,0x11,
                     0xb4,0x5e,0x4a,0x0e,0xe2,0x77,0xbf,0x1e,
                     0xfa,0x3b,0x8d,0xbd,0x55,0x00,0xcb,0x03,
                     0xc0,0xa7,0xb0,0xec,0x1c,0x00,0xa6,0x01,
                     0x93,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                     0x0a,0x07,0x8b,0x00,0x00,0x00,0x65,0x11,
                     0x8c,0x5e,0x4a,0x0e,0xc6,0x7a,0xbe,0x1e,
                     0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07,
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
                     0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set1_10bit(self):
        # Purpose: Encode a large data set using 16 bit word size
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(10, 257)
        test_ardecoder = ARDecoder(10, 257, 256)

        data = array('i',
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
                     0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07,256]) # 89

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set2_10bit(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(10, 257)
        test_ardecoder = ARDecoder(10, 257, 256)

        data = array('i',
                     [0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                     0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                     0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                     0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set3_10bit(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(10, 257)
        test_ardecoder = ARDecoder(10, 257, 256)

        data = array('i',
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
                     0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])

    def test_encode_decode_data_larger_set4_10bit(self):
        # Purpose: Encode a large data set
        # Expectation: The decoded data should match the original

        test_arencoder = AREncoder(10, 257)
        test_ardecoder = ARDecoder(10, 257, 256)

        data = array('i',
                     [0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                     0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                     0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                     0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                     0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                     0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                     0x00,0x00,0x00,0x00,
                     0x56,0xba,0x71,0xd5,0x98,0x3b,0x5f,0x2f,
                     0x56,0xba,0x71,0xd5,0x1c,0x00,0xa6,0x0e,
                     0xb4,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                     0x97,0x06,0xcb,0x00,0x00,0x00,0x68,0x11,
                     0xb4,0x5e,0x4a,0x0e,0xe2,0x77,0xbf,0x1e,
                     0xfa,0x3b,0x8d,0xbd,0x55,0x00,0xcb,0x03,
                     0xc0,0xa7,0xb0,0xec,0x1c,0x00,0xa6,0x01,
                     0x93,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                     0x0a,0x07,0x8b,0x00,0x00,0x00,0x65,0x11,
                     0x8c,0x5e,0x4a,0x0e,0xc6,0x7a,0xbe,0x1e,
                     0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07,
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
                     0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,256])

        inputDataLen = len(data)
        encodedData = bytearray(1024)
        decodedData = bytearray(1024)
        encodedDataSize = 0
        decodedDataSize = 0

        encodedDataSize = test_arencoder.encode(data, inputDataLen, encodedData, 1024)
        decodedDataSize = test_ardecoder.decode(encodedData,encodedDataSize,decodedData,1024)

        self.assertEqual(decodedDataSize, inputDataLen-1)

        for i in range(0,inputDataLen-1):
            self.assertEqual(data[i], decodedData[i])


if __name__ == '__main__':
    unittest.main()
