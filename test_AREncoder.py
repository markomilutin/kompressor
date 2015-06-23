__author__ = 'mmilutinovic'

import unittest
from AREncoder import AREncoder
from array import array

class TestAREncoder(unittest.TestCase):

    def test_instantiate_Arencoder_invalid_parameters(self):
        # Purpose: Instantiate object with invalid word size parameter
        # Expectation: An exception should be thrown

        with self.assertRaises(Exception):
            AREncoder(0, 257)

    def test_instantiate_Arencoder_valid(self):
        # Purpose: Instantiate kompressor with valid parameters
        # Expectation: The member variables should be initialized correctly

        test_encoder = AREncoder(11, 257)

        self.assertEqual(512, test_encoder.mMaxCompressionBytes)
        self.assertEqual(11, test_encoder.mWordSize)
        self.assertEqual(0x07FF, test_encoder.mWordBitMask)
        self.assertEqual(0x0400, test_encoder.mWordMSBMask)
        self.assertEqual(0x0200, test_encoder.mWordSecondMSBMask)
        self.assertNotEqual(None, test_encoder.mSymbolCumulativeCount)
        self.assertEqual(None, test_encoder.mEncodedData)

        self.assertEqual(257, test_encoder.mTotalSymbolCount)
        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(2047, test_encoder.mUpperTag)
        self.assertEqual(0, test_encoder.mE3ScaleCount)
        self.assertEqual(0, test_encoder.mCurrentBitCount)

        for i in range(0, test_encoder.mVocabularySize):
            self.assertEqual(1 + i, test_encoder.mSymbolCumulativeCount[i])

    def test_reset(self):
        # Purpose: Re-initialize the members
        # Expectation: Ensure that data is initialized properly

        test_encoder = AREncoder(11,256)

        test_encoder.mTotalSymbolCount = 49
        test_encoder.mEncodedDataCount = 33
        test_encoder.mLowerTag = 7
        test_encoder.mUpperTag = 9
        test_encoder.mE3ScaleCount = 99
        test_encoder.mCurrentByte = 0xFF
        test_encoder.mCurrentBitCount = 9

        # Initialize byte array to a count of one for each symbol
        for i in range(0, 256):
            test_encoder.mSymbolCumulativeCount[i] = 4

        test_encoder.reset();

        self.assertNotEqual(None, test_encoder.mSymbolCumulativeCount)
        self.assertEqual(None, test_encoder.mEncodedData)
        self.assertEqual(256, test_encoder.mTotalSymbolCount)
        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(2047, test_encoder.mUpperTag)
        self.assertEqual(0, test_encoder.mE3ScaleCount)
        self.assertEqual(0, test_encoder.mCurrentBitCount)

        # Initialize byte array to a count of one for each symbol
        for i in range(0, 256):
            self.assertEqual(1 + i, test_encoder.mSymbolCumulativeCount[i])


    def test_append_bitmax_not_reached(self):
        # Purpose: Append bits but ensure that the max of 8 is not exceeded
        # Expectation: The current byte should contain the passed in bits and the bit count should be correct

        test_encoder = AREncoder(11, 256)
        test_encoder.mEncodedData = bytearray(1024)

        test_encoder._append_bit(1)
        test_encoder._append_bit(0)
        test_encoder._append_bit(0)
        test_encoder._append_bit(1)
        test_encoder._append_bit(1)
        test_encoder._append_bit(0)
        test_encoder._append_bit(1)

        self.assertEqual(7, test_encoder.mCurrentBitCount)
        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0x4D, test_encoder.mEncodedData[0])
        self.assertEqual(0, test_encoder.mEncodedData[1])

    def test_append_bitmax_reached(self):
        # Purpose: Append bits up to max of 8
        # Expectation: The current byte should be 0 and the previous value should be in the compressed data byte array

        test_encoder = AREncoder(11, 256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        test_encoder._append_bit(1)
        test_encoder._append_bit(0)
        test_encoder._append_bit(0)
        test_encoder._append_bit(1)
        test_encoder._append_bit(1)
        test_encoder._append_bit(0)
        test_encoder._append_bit(1)
        test_encoder._append_bit(1)

        self.assertEqual(0, test_encoder.mCurrentBitCount)
        self.assertEqual(1, test_encoder.mEncodedDataCount)
        self.assertEqual(0x9B, test_encoder.mEncodedData[0])
        self.assertEqual(0, test_encoder.mEncodedData[1])

    def test_append_bit_past_one_byte(self):
        # Purpose: Append bits past max of 8 bits per byte
        # Expectation: The current byte should be based on bits past 8 and the previous value should be based on the first 8 bits

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        test_encoder._append_bit(1)
        test_encoder._append_bit(0)
        test_encoder._append_bit(0)
        test_encoder._append_bit(1)
        test_encoder._append_bit(1)
        test_encoder._append_bit(0)
        test_encoder._append_bit(1)
        test_encoder._append_bit(1)
        test_encoder._append_bit(1)
        test_encoder._append_bit(1)
        test_encoder._append_bit(1)
        test_encoder._append_bit(1)

        self.assertEqual(4, test_encoder.mCurrentBitCount)
        self.assertEqual(0x0F, test_encoder.mEncodedData[1])
        self.assertEqual(1, test_encoder.mEncodedDataCount)
        self.assertEqual(0x9B, test_encoder.mEncodedData[0])

    def test_append_bit_pastmax_byte(self):
        # Purpose: Append bits past max bytes
        # Expectation: An exception should be thrown

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(65536)
        test_encoder.mMaxEncodedDataLen = 65536

        self.assertEqual(65536, len(test_encoder.mEncodedData))

        # Fill up byte array
        for i in range(0, 65535*8):
            test_encoder._append_bit(1)

        test_encoder._append_bit(0)
        test_encoder._append_bit(0)
        test_encoder._append_bit(0)
        test_encoder._append_bit(0)
        test_encoder._append_bit(0)
        test_encoder._append_bit(0)
        test_encoder._append_bit(0)

        self.assertEqual(65536, len(test_encoder.mEncodedData))

        # Push it over the current max
        with self.assertRaises(Exception):
            test_encoder._append_bit(1)
            test_encoder._append_bit(1)

    def test_increment_count(self):
        # Purpose: Increment various indexes
        # Expectation: The cumulative counts will be updated appropriately

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        for i in range(0, 256):
            self.assertEqual(1 + i, test_encoder.mSymbolCumulativeCount[i])

        self.assertEqual(256, test_encoder.mSymbolCumulativeCount[255])
        self.assertEqual(256, test_encoder.mTotalSymbolCount)

        test_encoder._increment_count(0)

        for i in range(0, 256):
            self.assertEqual(2 + i, test_encoder.mSymbolCumulativeCount[i])

        self.assertEqual(257, test_encoder.mTotalSymbolCount)

        test_encoder._increment_count(50)
        self.assertEqual(258, test_encoder.mTotalSymbolCount)

        for i in range(0, 50):
            self.assertEqual(2 + i, test_encoder.mSymbolCumulativeCount[i])

        for i in range(50, 256):
            self.assertEqual(3 + i, test_encoder.mSymbolCumulativeCount[i])

        test_encoder._increment_count(50)
        self.assertEqual(259, test_encoder.mTotalSymbolCount)

        for i in range(0, 50):
            self.assertEqual(2 + i, test_encoder.mSymbolCumulativeCount[i])

        for i in range(50, 256):
            self.assertEqual(4 + i, test_encoder.mSymbolCumulativeCount[i])

        self.assertEqual(259, test_encoder.mSymbolCumulativeCount[255])

        test_encoder._increment_count(255)
        self.assertEqual(260, test_encoder.mTotalSymbolCount)

        for i in range(0, 50):
            self.assertEqual(2 + i, test_encoder.mSymbolCumulativeCount[i])

        for i in range(50, 255):
            self.assertEqual(4 + i, test_encoder.mSymbolCumulativeCount[i])

        self.assertEqual(260, test_encoder.mSymbolCumulativeCount[255])


    def test_increment_count_pastmax(self):
        # Purpose: Increment various indexes until we surpass the max bytes
        # Expectation: The stats should be normalized

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        for i in range(0, 256):
            self.assertEqual(1 + i, test_encoder.mSymbolCumulativeCount[i])

        for i in range(0, 100):
            test_encoder._increment_count(0)

        for i in range(0, 100):
            test_encoder._increment_count(200)

        self.assertEqual(456, test_encoder.mTotalSymbolCount)

        for i in range(0, 55):
            test_encoder._increment_count(255)

        self.assertEqual(511, test_encoder.mTotalSymbolCount)

        test_encoder._increment_count(255)

        # Normalization should occur now

        # Ensure each entry is greater than previous one which ensure that each symbol count is at least 0
        for i in range(1, 256):
            self.assertGreater(test_encoder.mSymbolCumulativeCount[i], test_encoder.mSymbolCumulativeCount[i-1])

        self.assertEqual(50, test_encoder.mSymbolCumulativeCount[0])
        self.assertEqual(50, test_encoder.mSymbolCumulativeCount[200] - test_encoder.mSymbolCumulativeCount[199])
        self.assertEqual(28, test_encoder.mSymbolCumulativeCount[255] - test_encoder.mSymbolCumulativeCount[254])

        self.assertEqual(381, test_encoder.mTotalSymbolCount)

    def test_rescale_none_required(self):
        # Purpose: Call when the lower and upper tag are in a range that requires no rescaling
        # Expectation: The tags should not be modified and no bits should be added to compressed data

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        test_encoder.mLowerTag = 510    # b00111111110 (just below quarter mark)
        test_encoder.mUpperTag = 1025   # b10000000001 (halfway point)

        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        test_encoder._rescale()

        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        self.assertEqual(510, test_encoder.mLowerTag)
        self.assertEqual(1025, test_encoder.mUpperTag)

    def test_rescale_E1_required(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E1 scaling
        # Expectation: The tags should be modified according to E1 and a 0 bit should be added to compressed data

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        test_encoder.mLowerTag = 0     # b00000000000 (0)
        test_encoder.mUpperTag = 1023  # b01111111111 (just below halfway point)

        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        test_encoder._rescale()

        self.assertEqual(1, test_encoder.mCurrentBitCount)
        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(2047, test_encoder.mUpperTag)

    def test_rescale_E1_required_with_E3ScaleCount(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E1 scaling and there is a count of 2 on the E3 Scale Count
        # Expectation: The tags should be modified according to E1 and a 0 bit should be added to compressed data. Two 0 bits should be added to compensate for E3 Scale Count

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        test_encoder.mLowerTag = 0      # b00000000000 (0)
        test_encoder.mUpperTag = 1022   # b01111111110 (just below halfway point)

        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        test_encoder.mE3ScaleCount = 2

        test_encoder._rescale()

        self.assertEqual(0, test_encoder.mE3ScaleCount)
        self.assertEqual(3, test_encoder.mCurrentBitCount)
        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(3, test_encoder.mEncodedData[0])

        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(2045, test_encoder.mUpperTag)

    def test_rescale_E1_requiredmultiple(self):
        # Purpose: Call when the lower and upper tag are in a range that requires multiple E1 scalings
        # Expectation: The tags should be modified according to E1 and a 0 bit should be added to compressed data as many times as E1 was performed

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        test_encoder.mLowerTag = 0    # b00000000000
        test_encoder.mUpperTag = 256  # b00100000000

        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        test_encoder._rescale()

        self.assertEqual(2, test_encoder.mCurrentBitCount)
        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(1027, test_encoder.mUpperTag)

    def test_rescale_E2_required(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E2 scaling
        # Expectation: The tags should be modified according to E2 and a 1 bit should be added to compressed data

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        test_encoder.mLowerTag = 1024   # b10000000000 (above halfway)
        test_encoder.mUpperTag = 2012   # b11111011100

        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        test_encoder._rescale()

        self.assertEqual(1, test_encoder.mCurrentBitCount)
        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(1, test_encoder.mEncodedData[0])

        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(1977, test_encoder.mUpperTag)

    def test_rescale_E2_required_with_E3ScaleCount(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E2 scaling and there is a count of 2 on the E3 Scale Count
        # Expectation: The tags should be modified according to E2 and a 1 bit should be added to compressed data. Two 0 bits should be added to compensate for E3 Scale Count

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        test_encoder.mLowerTag = 1024   # b10000000000 (above halfway)
        test_encoder.mUpperTag = 2012   # b11111011100

        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        test_encoder.mE3ScaleCount = 2

        test_encoder._rescale()

        self.assertEqual(0, test_encoder.mE3ScaleCount)
        self.assertEqual(3, test_encoder.mCurrentBitCount)
        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0x4, test_encoder.mEncodedData[0])

        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(1977, test_encoder.mUpperTag)

    def test_rescale_E2_requiredmultiple(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E2 scaling multiple times
        # Expectation: The tags should be modified according to E2 and a 1 bit should be added to compressed data for each scaling

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        test_encoder.mLowerTag = 1536   # b11000000000
        test_encoder.mUpperTag = 2047   # b11111111111

        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        test_encoder._rescale()

        self.assertEqual(2, test_encoder.mCurrentBitCount)
        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0x3, test_encoder.mEncodedData[0])

        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(2047, test_encoder.mUpperTag)

    def test_rescale_E3_required(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E3 scaling
        # Expectation: The tags should be modified according to E3 and the E3 scale count should be incremented

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        test_encoder.mLowerTag = 512    # b01000000000 (above quarter mark)
        test_encoder.mUpperTag = 1500   # b10111011100 (below 3 quarters mark

        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        test_encoder._rescale()

        self.assertEqual(0, test_encoder.mCurrentBitCount)
        self.assertEqual(1, test_encoder.mE3ScaleCount)
        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(1976, test_encoder.mUpperTag)

    def test_rescale_E3multiple(self):
        # Purpose: Call when the lower and upper tag are in a range that requires E3 scaling multiple times
        # Expectation: The tags should be modified by E3

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        test_encoder.mLowerTag = 812    # b01100101100
        test_encoder.mUpperTag = 1162   # b10010001010

        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        test_encoder._rescale()

        self.assertEqual(0, test_encoder.mCurrentBitCount)
        self.assertEqual(2, test_encoder.mE3ScaleCount)
        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        self.assertEqual(176, test_encoder.mLowerTag)
        self.assertEqual(1576, test_encoder.mUpperTag)

    def test_update_range_tags(self):
        # Purpose: Test updating the upper lower tags with incoming symbols
        # Expectation: The upper and lower tags should be updated correctly and the stat counts should be incremented appropriately

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        test_encoder.mLowerTag = 0
        test_encoder.mUpperTag = 2047

        self.assertEqual(0, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])

        # Pass in index for symbol 0x00 which currently has cumulative count of 1 out of total count of 256
        test_encoder._update_range_tags(0)

        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(7, test_encoder.mUpperTag)

        self.assertEqual(2, test_encoder.mSymbolCumulativeCount[0])
        self.assertEqual(257, test_encoder.mTotalSymbolCount)
        self.assertEqual(0, test_encoder.mEncodedDataCount)

        # _rescale
        test_encoder._rescale();

        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(2047, test_encoder.mUpperTag)

        self.assertEqual(2, test_encoder.mSymbolCumulativeCount[0])
        self.assertEqual(257, test_encoder.mTotalSymbolCount)
        self.assertEqual(1, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])
        self.assertEqual(0, test_encoder.mCurrentBitCount)

        # Pass in index for symbol 0x00 which currently has cumulative count of 2 out of total count of 257
        test_encoder._update_range_tags(0)

        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(14, test_encoder.mUpperTag)

        self.assertEqual(3, test_encoder.mSymbolCumulativeCount[0])
        self.assertEqual(258, test_encoder.mTotalSymbolCount)

        # _rescale
        test_encoder._rescale();

        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(1919, test_encoder.mUpperTag)

        self.assertEqual(3, test_encoder.mSymbolCumulativeCount[0])
        self.assertEqual(258, test_encoder.mTotalSymbolCount)
        self.assertEqual(1, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])
        self.assertEqual(0, test_encoder.mEncodedData[1])
        self.assertEqual(7, test_encoder.mCurrentBitCount)

        # Pass in index for symbol 0xAA which currently has cumulative count of count out of 173 total count of 258
        self.assertEqual(172, test_encoder.mSymbolCumulativeCount[0xA9])
        self.assertEqual(173, test_encoder.mSymbolCumulativeCount[0xAA])
        test_encoder._update_range_tags(0xAA)

        self.assertEqual(1280, test_encoder.mLowerTag)
        self.assertEqual(1286, test_encoder.mUpperTag)

        self.assertEqual(3, test_encoder.mSymbolCumulativeCount[0])
        self.assertEqual(172, test_encoder.mSymbolCumulativeCount[0xA9])
        self.assertEqual(174, test_encoder.mSymbolCumulativeCount[0xAA])
        self.assertEqual(259, test_encoder.mTotalSymbolCount)

        # _rescale
        test_encoder._rescale();

        self.assertEqual(0, test_encoder.mLowerTag)
        self.assertEqual(1791, test_encoder.mUpperTag)

        self.assertEqual(3, test_encoder.mSymbolCumulativeCount[0])
        self.assertEqual(172, test_encoder.mSymbolCumulativeCount[0xA9])
        self.assertEqual(174, test_encoder.mSymbolCumulativeCount[0xAA])
        self.assertEqual(259, test_encoder.mTotalSymbolCount)

        self.assertEqual(2, test_encoder.mEncodedDataCount)
        self.assertEqual(0, test_encoder.mEncodedData[0])
        self.assertEqual(1, test_encoder.mEncodedData[1])
        self.assertEqual(7, test_encoder.mCurrentBitCount)

    def test_normalize_stats(self):
        # Purpose: Normalize statistics across several ranges
        # Expectation: The cumulative counts should be correct after each normalization

        test_encoder = AREncoder(11,256)
        test_encoder.mEncodedData = bytearray(1024)
        test_encoder.mMaxEncodedDataLen = 1024

        # Normalize unchanged data, it should remain the same
        test_encoder._normalize_stats();

        self.assertEqual(256, test_encoder.mTotalSymbolCount)

        self.assertEqual(1, test_encoder.mSymbolCumulativeCount[0])
        self.assertEqual(2, test_encoder.mSymbolCumulativeCount[1])
        self.assertEqual(65, test_encoder.mSymbolCumulativeCount[64])
        self.assertEqual(251, test_encoder.mSymbolCumulativeCount[250])
        self.assertEqual(256, test_encoder.mSymbolCumulativeCount[255])


        for i in range(0, 256):
            self.assertEqual(1 + i, test_encoder.mSymbolCumulativeCount[i])

        # Normalize changed data, All count should be halved
        for i in range(0,10):
            test_encoder._increment_count(0)

        for i in range(0,10):
            test_encoder._increment_count(250)

        for i in range(0,10):
            test_encoder._increment_count(255)

        self.assertEqual(286, test_encoder.mTotalSymbolCount)

        test_encoder._normalize_stats();

        self.assertEqual(268, test_encoder.mTotalSymbolCount)

        self.assertEqual(5, test_encoder.mSymbolCumulativeCount[0])
        self.assertEqual(6, test_encoder.mSymbolCumulativeCount[1])
        self.assertEqual(69, test_encoder.mSymbolCumulativeCount[64])
        self.assertEqual(259, test_encoder.mSymbolCumulativeCount[250])
        self.assertEqual(268, test_encoder.mSymbolCumulativeCount[255])


    def test_encode_data_data_len_invalid(self):
        # Purpose: Pass in a data byte array that is smaller than the specified data length
        # Expectation: An exception should be thrown

        test_encoder = AREncoder(11,256)

        data = array('i', [0]*10)
        encodedData = bytearray(10)

        with self.assertRaises(Exception):
            test_encoder.encode(data, 11, encodedData, 10)

    def test_encode_data_compressed_data_len_invalid(self):
        # Purpose: Pass in a data byte array that is smaller than the specified data length
        # Expectation: An exception should be thrown

        test_encoder = AREncoder(11,256)

        data = array('i', [0]*10)
        encodedData = bytearray(10)

        with self.assertRaises(Exception):
            test_encoder.encode(data, 10, encodedData, 11)

    def test_encode_data_small_set(self):
        # Purpose: Encode the data set {0x00, 0x00, 0x01}
        # Expectation: The resulting encode data should be correct

        test_encoder = AREncoder(11,256)

        data = array('i', [0]*10)
        encodedData = bytearray(10)
        encodedDataSize = 0

        data[0] = 0x00
        data[1] = 0x00
        data[2] = 0x01

        encodedDataSize = test_encoder.encode(data, 3, encodedData, 10)

        self.assertEqual(5, encodedDataSize)
        self.assertEqual(0x00, encodedData[0])
        self.assertEqual(0x00, encodedData[1])
        self.assertEqual(0x05, encodedData[2])
        self.assertEqual(0x80, encodedData[3])
        self.assertEqual(0x00, encodedData[4])

    def test_encode_data_not_enough_space(self):
        # Purpose: Encode the data set {0x00, 0x00, 0x01} but set the compressed data byte array size to 1 which is not enough to hold the compressed data
        # Expectation: An exception should be raised

        test_encoder = AREncoder(11, 256)

        data = bytearray(10)
        encodedData = bytearray(10)
        encodedDataSize = 0

        data[0] = 0x00
        data[1] = 0x00
        data[2] = 0x01

        with self.assertRaises(Exception):
            test_encoder.encode(data, 3, encodedData, 1)

    def test_encoded_data(self):
        # Purpose: Compress several different data sets
        # Expectation: Ensure that the data gets encoded

        test_encoder = AREncoder(11,256)

        test_data = bytearray([0x56,0xba,0x71,0xd5,0x98,0x3b,0x5f,0x2f,
                               0x56,0xba,0x71,0xd5,0x1c,0x00,0xa6,0x0e,
                               0xb4,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                               0x97,0x06,0xcb,0x00,0x00,0x00,0x68,0x11,
                               0xb4,0x5e,0x4a,0x0e,0xe2,0x77,0xbf,0x1e,
                               0xfa,0x3b,0x8d,0xbd,0x55,0x00,0xcb,0x03,
                               0xc0,0xa7,0xb0,0xec,0x1c,0x00,0xa6,0x01,
                               0x93,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                               0x0a,0x07,0x8b,0x00,0x00,0x00,0x65,0x11,
                               0x8c,0x5e,0x4a,0x0e,0xc6,0x7a,0xbe,0x1e,
                               0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07])
        test_data1 = bytearray([0x56,0xba,0x71,0xd5,0x1c,0x00,0xa6,0x0e,
                               0xb4,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                               0x97,0x06,0xcb,0x00,0x00,0x00,0x68,0x11,
                               0xb4,0x5e,0x4a,0x0e,0xe2,0x77,0xbf,0x1e,
                               0xfa,0x3b,0x8d,0xbd,0x55,0x00,0xcb,0x03,
                               0xc0,0xa7,0xb0,0xec,0x1c,0x00,0xa6,0x01,
                               0x93,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                               0x0a,0x07,0x8b,0x00,0x00,0x00,0x65,0x11,
                               0x8c,0x5e,0x4a,0x0e,0xc6,0x7a,0xbe,0x1e,
                               0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07])

        test_data2 = bytearray([0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                                0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                                0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                                0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                                0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                                0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                                0x00,0x00,0x00,0x00])
        test_data3 = bytearray([0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                                0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                                0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                                0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                                0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                                0x00,0x00,0x00,0x00])
        test_data4 = bytearray([0xfb,0xbb,0x71,0xd5,0x98,0x0d,0x46,0x8c,
                                0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03])
        test_data5 = bytearray([0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
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
                                0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03])

        encodedData = bytearray(1024)

        encodedDataLen1 = test_encoder.encode(test_data, 88, encodedData, 1024)
        self.assertGreater(88, encodedDataLen1)

        test_encoder.reset()
        encodedDataLen2 = test_encoder.encode(test_data1, 80, encodedData, 1024)
        self.assertGreater(80, encodedDataLen2)

        test_encoder.reset()
        encodedDataLen3 = test_encoder.encode(test_data2, 60, encodedData, 1024)
        self.assertGreater(60, encodedDataLen3)

        test_encoder.reset()
        encodedDataLen4 = test_encoder.encode(test_data3, 52, encodedData, 1024)
        self.assertGreater(52, encodedDataLen4)

        test_encoder.reset()
        encodedDataLen5 = test_encoder.encode(test_data4, 88, encodedData, 1024)
        self.assertGreater(88, encodedDataLen5)

        test_encoder.reset()
        encodedDataLen6 = test_encoder.encode(test_data5, 160, encodedData, 1024)
        self.assertGreater(160, encodedDataLen6)

    def test_encode_12bitword(self):
        # Purpose: Compress several different data sets using 12 bit word
        # Expectation: Ensure that the data gets compressed

        test_encoder = AREncoder(12, 256)

        test_data = bytearray([0x56,0xba,0x71,0xd5,0x98,0x3b,0x5f,0x2f,
                               0x56,0xba,0x71,0xd5,0x1c,0x00,0xa6,0x0e,
                               0xb4,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                               0x97,0x06,0xcb,0x00,0x00,0x00,0x68,0x11,
                               0xb4,0x5e,0x4a,0x0e,0xe2,0x77,0xbf,0x1e,
                               0xfa,0x3b,0x8d,0xbd,0x55,0x00,0xcb,0x03,
                               0xc0,0xa7,0xb0,0xec,0x1c,0x00,0xa6,0x01,
                               0x93,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                               0x0a,0x07,0x8b,0x00,0x00,0x00,0x65,0x11,
                               0x8c,0x5e,0x4a,0x0e,0xc6,0x7a,0xbe,0x1e,
                               0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07])
        test_data1 = bytearray([0x56,0xba,0x71,0xd5,0x1c,0x00,0xa6,0x0e,
                               0xb4,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                               0x97,0x06,0xcb,0x00,0x00,0x00,0x68,0x11,
                               0xb4,0x5e,0x4a,0x0e,0xe2,0x77,0xbf,0x1e,
                               0xfa,0x3b,0x8d,0xbd,0x55,0x00,0xcb,0x03,
                               0xc0,0xa7,0xb0,0xec,0x1c,0x00,0xa6,0x01,
                               0x93,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                               0x0a,0x07,0x8b,0x00,0x00,0x00,0x65,0x11,
                               0x8c,0x5e,0x4a,0x0e,0xc6,0x7a,0xbe,0x1e,
                               0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07])

        test_data2 = bytearray([0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                                0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                                0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                                0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                                0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                                0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                                0x00,0x00,0x00,0x00])
        test_data3 = bytearray([0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                                0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                                0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                                0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                                0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                                0x00,0x00,0x00,0x00])
        test_data4 = bytearray([0xfb,0xbb,0x71,0xd5,0x98,0x0d,0x46,0x8c,
                                0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03])
        test_data5 = bytearray([0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
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
                                0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03])

        encodedData = bytearray(1024)

        encodedDataLen1 = test_encoder.encode(test_data, 88, encodedData, 1024)
        self.assertGreater(88, encodedDataLen1)

        test_encoder.reset()
        encodedDataLen2 = test_encoder.encode(test_data1, 80, encodedData, 1024)
        self.assertGreater(80, encodedDataLen2)

        test_encoder.reset()
        encodedDataLen3 = test_encoder.encode(test_data2, 60, encodedData, 1024)
        self.assertGreater(60, encodedDataLen3)

        test_encoder.reset()
        encodedDataLen4 = test_encoder.encode(test_data3, 52, encodedData, 1024)
        self.assertGreater(52, encodedDataLen4)

        test_encoder.reset()
        encodedDataLen5 = test_encoder.encode(test_data4, 88, encodedData, 1024)
        self.assertGreater(88, encodedDataLen5)

        test_encoder.reset()
        encodedDataLen6 = test_encoder.encode(test_data5, 160, encodedData, 1024)
        self.assertGreater(160, encodedDataLen6)

    def test_encode_16bitword(self):
        # Purpose: Compress several different data sets using 12 bit word
        # Expectation: Ensure that the data gets compressed

        test_encoder = AREncoder(16,256)

        test_data = bytearray([0x56,0xba,0x71,0xd5,0x98,0x3b,0x5f,0x2f,
                               0x56,0xba,0x71,0xd5,0x1c,0x00,0xa6,0x0e,
                               0xb4,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                               0x97,0x06,0xcb,0x00,0x00,0x00,0x68,0x11,
                               0xb4,0x5e,0x4a,0x0e,0xe2,0x77,0xbf,0x1e,
                               0xfa,0x3b,0x8d,0xbd,0x55,0x00,0xcb,0x03,
                               0xc0,0xa7,0xb0,0xec,0x1c,0x00,0xa6,0x01,
                               0x93,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                               0x0a,0x07,0x8b,0x00,0x00,0x00,0x65,0x11,
                               0x8c,0x5e,0x4a,0x0e,0xc6,0x7a,0xbe,0x1e,
                               0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07])
        test_data1 = bytearray([0x56,0xba,0x71,0xd5,0x1c,0x00,0xa6,0x0e,
                               0xb4,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                               0x97,0x06,0xcb,0x00,0x00,0x00,0x68,0x11,
                               0xb4,0x5e,0x4a,0x0e,0xe2,0x77,0xbf,0x1e,
                               0xfa,0x3b,0x8d,0xbd,0x55,0x00,0xcb,0x03,
                               0xc0,0xa7,0xb0,0xec,0x1c,0x00,0xa6,0x01,
                               0x93,0x5e,0x4a,0x0e,0xf5,0x01,0x00,0x00,
                               0x0a,0x07,0x8b,0x00,0x00,0x00,0x65,0x11,
                               0x8c,0x5e,0x4a,0x0e,0xc6,0x7a,0xbe,0x1e,
                               0x03,0x3a,0x8d,0xbd,0x0e,0x00,0x8b,0x07])

        test_data2 = bytearray([0xfb,0xbb,0x71,0xd5,0x98,0x00,0xca,0x6c,
                                0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                                0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                                0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                                0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                                0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                                0x00,0x00,0x00,0x00])
        test_data3 = bytearray([0x86,0xaa,0xb0,0xec,0x28,0x00,0x86,0x01,
                                0x94,0xd9,0x48,0x0e,0x03,0x08,0x99,0x00,
                                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                                0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,
                                0x00,0x08,0x00,0x02,0x68,0x00,0x03,0x52,
                                0x01,0x4c,0x4e,0x39,0x00,0x00,0x00,0x00,
                                0x00,0x00,0x00,0x00])
        test_data4 = bytearray([0xfb,0xbb,0x71,0xd5,0x98,0x0d,0x46,0x8c,
                                0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                                0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                                0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                                0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                                0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                                0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                                0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                                0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                                0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03])
        test_data5 = bytearray([0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
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
                                0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03])

        encodedData = bytearray(1024)

        encodedDataLen1 = test_encoder.encode(test_data, 88, encodedData, 1024)
        self.assertGreater(88, encodedDataLen1)

        test_encoder.reset()
        encodedDataLen2 = test_encoder.encode(test_data1, 80, encodedData, 1024)
        self.assertGreater(80, encodedDataLen2)

        test_encoder.reset()
        encodedDataLen3 = test_encoder.encode(test_data2, 60, encodedData, 1024)
        self.assertGreater(60, encodedDataLen3)

        test_encoder.reset()
        encodedDataLen4 = test_encoder.encode(test_data3, 52, encodedData, 1024)
        self.assertGreater(52, encodedDataLen4)

        test_encoder.reset()
        encodedDataLen5 = test_encoder.encode(test_data4, 88, encodedData, 1024)
        self.assertGreater(88, encodedDataLen5)

        test_encoder.reset()
        encodedDataLen6 = test_encoder.encode(test_data5, 160, encodedData, 1024)
        self.assertGreater(160, encodedDataLen6)

if __name__ == '__main__':
    unittest.main()

