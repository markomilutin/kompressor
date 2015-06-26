__author__ = 'Marko Milutinovic'

"""
This class will implement an Arithmetic Coding encoder
"""

import array
import utils
import math

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

        # Reset all the
        self.reset()

    def reset(self):
        """
        Reset all member variables that are not constant for the duration of the object life

        :return: None
        """

        self.mEncodedData = None
        self.mMaxEncodedDataLen = 0                                                # The max number of bytes that can be stored in mEncodedData
        self.mEncodedDataCount = int(0)                                            # The number of bytes compressed data is taking up
        self.mTotalSymbolCount = self.mVocabularySize                              # The total number of symbols encountered
        self.mE3ScaleCount = 0                                                     # Holds the number of E3 mappings currently outstanding
        self.mCurrentBitCount = 0                                                  # The current number of bits loaded onto the mCurrentByte variable

        # We are initializing with an assumption of a value of 1 for the count of each symbol. The initial cumulative count data will just be an incrementing series up to vocabulary size
        for i in range(0,self.mVocabularySize):
            self.mSymbolCumulativeCount[i] = (i + 1)

        # Initialize the range tags to min and max
        self.mLowerTag = 0
        self.mUpperTag = self.mWordBitMask

    def _append_bit(self, bitValue_):
        """
        Take the incoming bit and append it to the mCurrentByte. Once 8 bits have been appended move to the next
        index of the compressed data array

        :param bitValue: The bit to be appended to the current outstanding compression byte
        :return: None
        """

        # Store the current bit onto the pending byte
        self.mEncodedData[self.mEncodedDataCount] = ((self.mEncodedData[self.mEncodedDataCount] << 1) | bitValue_) & 0xFF

        # Increment the count of bits stored
        self.mCurrentBitCount += 1

        # If max number of bits have been appended, move to compressed data byte array
        if(self.mCurrentBitCount == 8):
            self.mEncodedDataCount += 1

            # If there is no more room throw exception
            if(self.mEncodedDataCount >= self.mMaxEncodedDataLen):
                raise Exception('Out of space')

            self.mCurrentBitCount = 0
            self.mEncodedData[self.mEncodedDataCount] = int(0)

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

        self.mTotalSymbolCount += 1

        # If we have reached the max number of bytes, we need to normalize the stats to allow us to continue
        if(self.mTotalSymbolCount >= self.mMaxCompressionBytes):
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

        sameMSB = ((self.mLowerTag & self.mWordMSBMask) == (self.mUpperTag & self.mWordMSBMask))
        valueMSB = ((self.mLowerTag & self.mWordMSBMask) >> (self.mWordSize -1)) & 0x0001
        tagRangeInMiddle = (((self.mUpperTag & self.mWordSecondMSBMask) == 0) and ((self.mLowerTag & self.mWordSecondMSBMask) == self.mWordSecondMSBMask))


        while(sameMSB or tagRangeInMiddle):

            # If the first bit is the same we need to perform E1 or E2 scaling. The same set of steps applies to both. If the range is in the middle we need to perform E3 scaling
            if(sameMSB):
                self._append_bit(valueMSB)
                self.mLowerTag = (self.mLowerTag << 1) & self.mWordBitMask
                self.mUpperTag = ((self.mUpperTag << 1) | 0x0001) & self.mWordBitMask

                while(self.mE3ScaleCount > 0):
                    self._append_bit((~valueMSB) & 0x0001)
                    self.mE3ScaleCount -= 1

            elif(tagRangeInMiddle):
                self.mLowerTag = (self.mLowerTag << 1) & self.mWordBitMask
                self.mUpperTag = (self.mUpperTag << 1) & self.mWordBitMask

                self.mLowerTag = ((self.mLowerTag & (~self.mWordMSBMask)) | ((~self.mLowerTag) & self.mWordMSBMask))
                self.mUpperTag = ((self.mUpperTag & (~self.mWordMSBMask)) | ((~self.mUpperTag) & self.mWordMSBMask))

                self.mE3ScaleCount += 1


            sameMSB = ((self.mLowerTag & self.mWordMSBMask) == (self.mUpperTag & self.mWordMSBMask))
            valueMSB = ((self.mLowerTag & self.mWordMSBMask) >> (self.mWordSize -1)) & 0x0001
            tagRangeInMiddle = (((self.mUpperTag & self.mWordSecondMSBMask) == 0) and ((self.mLowerTag & self.mWordSecondMSBMask) == self.mWordSecondMSBMask))

    def _rescale2(self, lowerTag_, upperTag_):
        """
        Currently HACK code to get multi stage encoding workin. Original function should be replaced to be usuable in all cases

        Perform required rescale operation on the upper and lower tags. The following scaling operations are pefromed:
            E1: both the upper and lower ranges fall into the bottom half of full range [0, 0.5). First bit is 0 for both.
                Shift out MSB for both and shift in 1 for upper tag and 0 for lower tag
            E2: both the upper and lower ranges fall into the top half of full range [0.5, 1). First bit is 1 for both.
                Shift out MSB for both and shift in 1 for upper tag and 0 for lower tag
            E3: the upper and lower tag interval lies in the middle [0.25, 0.75). The second MSB of upper tag is 0 and the second bit of the lower tag is 1.
                Complement second MSB bit of both and shift in 1 for upper tag and 0 for lower tag. Keep track of consecutive E3 scalings

        This version of the function will add to outgoing data but will not update any member variables except mE3ScaleCount, so the operation will not reflected in the statistics
        :return: The new values for lower and upper tag [lower, upper]
        """

        sameMSB = ((lowerTag_ & self.mWordMSBMask) == (upperTag_ & self.mWordMSBMask))
        valueMSB = ((lowerTag_ & self.mWordMSBMask) >> (self.mWordSize -1)) & 0x0001
        tagRangeInMiddle = (((upperTag_ & self.mWordSecondMSBMask) == 0) and ((lowerTag_ & self.mWordSecondMSBMask) == self.mWordSecondMSBMask))


        while(sameMSB or tagRangeInMiddle):

            # If the first bit is the same we need to perform E1 or E2 scaling. The same set of steps applies to both. If the range is in the middle we need to perform E3 scaling
            if(sameMSB):
                self._append_bit(valueMSB)
                lowerTag_ = (lowerTag_ << 1) & self.mWordBitMask
                upperTag_ = ((upperTag_ << 1) | 0x0001) & self.mWordBitMask

                while(self.mE3ScaleCount > 0):
                    self._append_bit((~valueMSB) & 0x0001)
                    self.mE3ScaleCount -= 1

            elif(tagRangeInMiddle):
                lowerTag_ = (lowerTag_ << 1) & self.mWordBitMask
                upperTag_ = (upperTag_ << 1) & self.mWordBitMask

                lowerTag_ = ((lowerTag_ & (~self.mWordMSBMask)) | ((~lowerTag_) & self.mWordMSBMask))
                upperTag_ = ((upperTag_ & (~self.mWordMSBMask)) | ((~upperTag_) & self.mWordMSBMask))

                self.mE3ScaleCount += 1


            sameMSB = ((lowerTag_ & self.mWordMSBMask) == (upperTag_ & self.mWordMSBMask))
            valueMSB = ((lowerTag_ & self.mWordMSBMask) >> (self.mWordSize -1)) & 0x0001
            tagRangeInMiddle = (((upperTag_ & self.mWordSecondMSBMask) == 0) and ((lowerTag_ & self.mWordSecondMSBMask) == self.mWordSecondMSBMask))

        return [lowerTag_, upperTag_]


    def _update_range_tags(self, newSymbolIndex_):
        """
        Update the upper and lower tags according to stats for the incoming symbol

        :param newSymbol_: Current symbol being encoded
        :return:
        """

        prevLowerTag = self.mLowerTag
        prevUpperTag = self.mUpperTag
        rangeDiff = prevUpperTag - prevLowerTag
        cumulativeCountSymbol = self.mSymbolCumulativeCount[newSymbolIndex_]
        cumulativeCountPrevSymbol = 0

        # If this is not the first index then set the previous symbol count to actual value
        if(newSymbolIndex_ >= 1):
            cumulativeCountPrevSymbol = self.mSymbolCumulativeCount[newSymbolIndex_-1]

        self.mLowerTag = int((prevLowerTag + math.floor(((rangeDiff + 1)*cumulativeCountPrevSymbol))/self.mTotalSymbolCount))
        self.mUpperTag = int((prevLowerTag + math.floor(((rangeDiff + 1)*cumulativeCountSymbol))/self.mTotalSymbolCount - 1))

        self._increment_count(newSymbolIndex_)

    def _update_range_tags2(self, newSymbolIndex_, lowerTag_, upperTag_):
        """
        Currently HACK code to get multi stage encoding workin. Original function should be replaced to be usuable in all cases

        Update the passed in upper and lower tags based on the incoming symbol index. Do not update any other member variables

        :param newSymbol_: Current symbol being encoded
        :param lowerTag_: lower tag that needs to be updated
        :param upperTag_: upper tag that needs to be updated
        :return: Returns the updated lower and upper tags, [lowerTag_, upperTag_]
        """

        prevLowerTag = lowerTag_
        prevUpperTag = upperTag_
        rangeDiff = prevUpperTag - prevLowerTag
        cumulativeCountSymbol = self.mSymbolCumulativeCount[newSymbolIndex_]
        cumulativeCountPrevSymbol = 0

        # If this is not the first index then set the previous symbol count to actual value
        if(newSymbolIndex_ >= 1):
            cumulativeCountPrevSymbol = self.mSymbolCumulativeCount[newSymbolIndex_-1]

        lowerTag_ = int((prevLowerTag + math.floor(((rangeDiff + 1)*cumulativeCountPrevSymbol))/self.mTotalSymbolCount))
        upperTag_ = int((prevLowerTag + math.floor(((rangeDiff + 1)*cumulativeCountSymbol))/self.mTotalSymbolCount - 1))

        return [lowerTag_, upperTag_]

    def _normalize_stats(self):
        """
        Divide the total count for each vocabulary by 2, the new value must be at least one. Use the cumulative
        vocabulary counts to accomplish this, Get new total symbol count from the entries

        :return: None
        """

        self.mTotalSymbolCount = 0
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

            self.mTotalSymbolCount += indexCount

    def encode(self, dataToEncode_, dataLen_, encodedData_, maxEncodedDataLen_, lastDataBlock=True):
        """
        Encode the data passed in. The encoded data will be stored in encodedData_ and if there is not enough room an
        exception will be thrown. Encoding statistics will not be reset when this function is called. It is up-to the caller
        to ensure that statistics are initialized properly if required.

        :param dataToEncode_: The data that needs to be compressed (integer array)
        :param dataLen_: The length of data that needs to be compressed
        :param encodedData_: The compressed data should be stored in this byte array
        :param maxEncodedDataLen_ : The max length of compressed data that can be stored in encodedData_

        :return: The number of bytes stored in encodedData_
        """

        # If the byte array is smaller than data length pass in throw exception
        if(len(dataToEncode_) < dataLen_):
            raise Exception("Data byte array passed in smaller than expected")

        # If the byte array is smaller than data length pass in throw exception
        if(len(encodedData_) < maxEncodedDataLen_):
            raise Exception("Encoded data byte array passed in smaller than expected")

        self.mEncodedData = encodedData_
        self.mEncodedDataCount = 0
        self.mCurrentBitCount = 0
        self.mMaxEncodedDataLen = maxEncodedDataLen_

        # Go through and compress data one byte at a time
        for i in range(0, dataLen_):
            self._update_range_tags(dataToEncode_[i])
            self._rescale()

        lowerTagToSend = self.mLowerTag

        # If not last data block insert extra symbol so that we can properly carry over on decoder. The decoder must be able to fully process the last symbol in order to work properly.
        # As data is transferred in bytes (not bits) there remains the possibility of extra 0 bits after data has ended which will confuse the decoder. If the last symbol encoded is a don't care then the decoder will properly pick up the actual last symbol.
        # The last symbol can't be reflected in the statistics as it will be thrown away on the decoder side
        if(lastDataBlock == False):
            [lower, upper] = self._update_range_tags2(0, self.mLowerTag, self.mUpperTag)
            [lower, upper] = self._rescale2(lower, upper)
            lowerTagToSend = lower

        # Store the current state of the lower tag to mark the completion of the compression
        for i in range(0, self.mWordSize):
            bitValue = (lowerTagToSend >> ((self.mWordSize - 1) - i)) & 0x0001

            self._append_bit(bitValue)

            # Ensure we account for any E3 scaling
            while(self.mE3ScaleCount > 0):
                self._append_bit((~bitValue) & 0x0001)
                self.mE3ScaleCount -= 1

        # Ensure that the current byte is added to the compressed data length if there are any outstanding bits on it
        if(self.mCurrentBitCount != 0):
            self.mEncodedDataCount += 1

        return self.mEncodedDataCount