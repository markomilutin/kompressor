__author__ = 'Marko Milutinovic'

"""
This class will implement an Arithmetic Coding encoder
"""

import array
import utils

class AREncoder:
    def __init__(self, wordSize_, vocabularySize_):
        """
        Initialize the object. The word size must be greater than 2 and less than or equal to 32

        :param wordSize_: The word size (bits) that will be used for encoding. Must be greater than 2 and less than or equal to 32
        :param vocabularySize_: The size of the vocabulary. Symbols run from 0 to (vocabularySize_ - 1)
        :return:
        """
        self.mMaxCompressionBytes = utils.calculateMaxBytes(wordSize_)                                 # The max number of bytes we can compress before the statistics need to be re-normalized
        self.mVocabularySize = vocabularySize_
        if(self.mMaxCompressionBytes == 0):
            raise Exception("Invalid word size specified")

        self.mWordSize = wordSize_                                                                 # The tag word size
        self.mWordBitMask = 0x0000                                                                 # The word size bit-mask
        self.mWordMSBMask = (0x0000 | (1 << (self.mWordSize - 1)))                                # The bit mask for the top bit of the word
        self.mWordSecondMSBMask = (0x0000 | (1 << (self.mWordSize - 2)))                          # The bit mask for the second most significant bit of the word

        # Create bit mask for the word size
        for i in range(0, self.mWordSize):
            self.mWordBitMask = (self.mWordBitMask << 1) | 0x0001

        # We are initializing with an assumption of a value of 1 for the count of each symbol. The initial cumulative count data will just be an incrementing series up to vocabulary size
        self.mSymbolCumulativeCount = array.array('i', range(1, self.mVocabularySize + 1))         # Hold current count of symbols encountered
        self.mCompressedData = None

        # Reset all the
        self._init_members()

    def _init_members(self):
        """
        Reset all member variables that are not constant for the duration of the object life

        :return: None
        """

        self.mCompressedDataCount = int(0)                                         # The number of bytes compressed data is taking up
        self._mTotalSymbolCount = self.mVocabularySize                              # The total number of symbols encountered
        self._mLowerTag = 0                                                         # The lower tag threshold
        self._mUpperTag = 0                                                         # The upper tag threshold
        self._mE3ScaleCount = 0                                                     # Holds the number of E3 mappings currently outstanding
        self._mCurrentBitCount = 0                                                  # The current number of bits loaded onto the _mCurrentByte variable

        # We are initializing with an assumption of a value of 1 for the count of each symbol. The initial cumulative count data will just be an incrementing series up to vocabulary size
        for i in range(0,self.mVocabularySize):
            self.mSymbolCumulativeCount[i] = (i + 1)

    def _append_bit(self, bitValue_):
        """
        Take the incoming bit and append it to the _mCurrentByte. Once 8 bits have been appended move to the next
        index of the compressed data array

        :param bitValue: The bit to be appended to the current outstanding compression byte
        :return: None
        """

        # Store the current bit onto the pending byte
        self.mCompressedData[self.mCompressedDataCount] = ((self.mCompressedData[self.mCompressedDataCount] << 1) | bitValue_) & 0xFF

        # Increment the count of bits stored
        self._mCurrentBitCount += 1

        # If max number of bits have been appended, move to compressed data byte array
        if(self._mCurrentBitCount == 8):
            self.mCompressedDataCount += 1

            # If there is no more room extend the bytearray by BASE_OUT_SIZE bytes
            if(self.mCompressedDataCount >= len(self.mCompressedData)):
                self.mCompressedData.extend(bytearray(self.BASE_OUT_SIZE))

            self._mCurrentBitCount = 0
            self.mCompressedData[self.mCompressedDataCount] = int(0)

    def _increment_count(self, indexToIncrement_):
        """
        Update the count for the provided index. We need to adjust all cumulative values above this index by one. Update
        the total symbol count as well. If we exceed the max symbol count normalize the stats

        :param indexToIncrement_: The index which we are updating
        :return: None
        """

        cumulativeCountValues = self.mSymbolCumulativeCount
        vocabularySize = self.mVocabularySize

        for i in range(indexToIncrement_, vocabularySize):
            cumulativeCountValues[i] += 1

        self._mTotalSymbolCount += 1

        # If we have reached the max number of bytes, we need to normalize the stats to allow us to continue
        if(self._mTotalSymbolCount >= self._mMaxCompressionBytes):
            self._normalize_stats()

    def _rescale(self):
        """
        Perform required rescale operation on the upper and lower tags. The following scaling operations are pefromed:
            E1: both the upper and lower ranges fall into the bottom half of full range [0, 0.5). First bit is 0 for both.
                Shift out MSB for both and shift in 1 for upper tag and 0 for lower tag
            E2: both the upper and lower ranges fall into the top half of full range [0.5, 1). First bit is 1 for both.
                Shift out MSB for both and shift in 1 for upper tag and 0 for lower tag
            E3: the upper and lower tag interval lies in the middle [0.25, 0.75). The second MSB of upper tag is 0 and the second bit of the lower tag is 1.
                Complement second MSB bit of both and shift in 1 for upper tag and 0 for lower tag. Keep track of consecutive E3 scalings
        :return:None
        """

        sameMSB = ((self._mLowerTag & self._mWordMSBMask) == (self._mUpperTag & self._mWordMSBMask))
        valueMSB = ((self._mLowerTag & self._mWordMSBMask) >> (self._mWordSize -1)) & 0x0001
        tagRangeInMiddle = (((self._mUpperTag & self._mWordSecondMSBMask) == 0) and ((self._mLowerTag & self._mWordSecondMSBMask) == self._mWordSecondMSBMask))


        while(sameMSB or tagRangeInMiddle):

            # If the first bit is the same we need to perform E1 or E2 scaling. The same set of steps applies to both. If the range is in the middle we need to perform E3 scaling
            if(sameMSB):
                self._append_bit(valueMSB)
                self._mLowerTag = (self._mLowerTag << 1) & self._mWordBitMask
                self._mUpperTag = ((self._mUpperTag << 1) | 0x0001) & self._mWordBitMask

                while(self._mE3ScaleCount > 0):
                    self._append_bit((~valueMSB) & 0x0001)
                    self._mE3ScaleCount -= 1

            elif(tagRangeInMiddle):
                self._mLowerTag = (self._mLowerTag << 1) & self._mWordBitMask
                self._mUpperTag = (self._mUpperTag << 1) & self._mWordBitMask

                self._mLowerTag = ((self._mLowerTag & (~self._mWordMSBMask)) | ((~self._mLowerTag) & self._mWordMSBMask))
                self._mUpperTag = ((self._mUpperTag & (~self._mWordMSBMask)) | ((~self._mUpperTag) & self._mWordMSBMask))

                self._mE3ScaleCount += 1


            sameMSB = ((self._mLowerTag & self._mWordMSBMask) == (self._mUpperTag & self._mWordMSBMask))
            valueMSB = ((self._mLowerTag & self._mWordMSBMask) >> (self._mWordSize -1)) & 0x0001
            tagRangeInMiddle = (((self._mUpperTag & self._mWordSecondMSBMask) == 0) and ((self._mLowerTag & self._mWordSecondMSBMask) == self._mWordSecondMSBMask))

    def _update_range_tags(self, newSymbolIndex_):
        """ Update the upper and lower tags according to stats for the incoming symbol

        :param newSymbol_: Current symbol being encoded
        :return:
        """

        prevLowerTag = self._mLowerTag
        prevUpperTag = self._mUpperTag
        rangeDiff = prevUpperTag - prevLowerTag
        cumulativeCountSymbol = self.mSymbolCumulativeCount[newSymbolIndex_]
        cumulativeCountPrevSymbol = 0

        # If this is not the first index then set the previous symbol count to actual value
        if(newSymbolIndex_ >= 1):
            cumulativeCountPrevSymbol = self.mSymbolCumulativeCount[newSymbolIndex_-1]

        self._mLowerTag = int((prevLowerTag + math.floor(((rangeDiff + 1)*cumulativeCountPrevSymbol))/self._mTotalSymbolCount))
        self._mUpperTag = int((prevLowerTag + math.floor(((rangeDiff + 1)*cumulativeCountSymbol))/self._mTotalSymbolCount - 1))

        self._increment_count(newSymbolIndex_)

    def _normalize_stats(self):
        """ Divide the total count for each vocabulary by 2, the new value must be at least one. Use the cumulative
            vocabulary counts to accomplish this, Get new total symbol count from the entries

        :return: None
        """

        self._mTotalSymbolCount = 0
        prevOldCumulativeCount = 0

        # Go through all the entries in the cumulative count array
        for i in range(0, self.mVocabularySize):

            # If it's not the first index get the difference between cumulative counts to get the actual count
            if(i != 0):
                indexCount = self.mSymbolCumulativeCount[i] - prevOldCumulativeCount
            else:
                indexCount = self.mSymbolCumulativeCount[i]

            prevOldCumulativeCount = self.mSymbolCumulativeCount[i]

            indexCount = int(indexCount/2)

            # Has to be at least one
            if(indexCount == 0):
                indexCount = 1

            # If it's not the first index use the previous index value to get the current cumulative count
            if(i != 0):
                self.mSymbolCumulativeCount[i] = self.mSymbolCumulativeCount[i-1] + indexCount
            else:
                self.mSymbolCumulativeCount[i] = indexCount

            self._mTotalSymbolCount += indexCount


    def _compressSymbol(self, symbol):
        """ Compress each incoming symbol by updating the range tags to encode this symbol and rescaling

        :param symbol: The symbol to be encoded
        :return:
        """
        self._update_range_tags(symbol)
        self._rescale()

    def encode(self, dataToEncode_, dataLen_, encodedData_, maxEncodedDataLen_):
        """
        Encode the data one byte at a time.

        :param dataToEncode_: The data that needs to be compressed (integer array)
        :param dataLen_: The length of data that needs to be compressed
        :param encodedData_: The compressed data should be stored in this byte array
        :param maxEncodedDataLen_ : The max length of compressed data that can be stored in compressesdData_

        :return: The number of bytes stored in encodedData_
        """
        pass

    def reset(self):
        """
        Reset the encoder statistics

        :return:
        """
        pass


