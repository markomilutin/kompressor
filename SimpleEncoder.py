__author__ = 'Marko Milutinovic'

"""
This class is meant for testing. It implements a simple encoder that will simply store the passed in
data into array of integers. The symbols run from 0 to the vocabulary size - 1
"""

from array import *

class SimpleEncoder:
    def __init__(self, vocabularySize_):
        """
        Initialize the vocabulary size based on incoming parameter and initialize the integer array where
        data will be stored

        :param vocabularySize_: the vocabulary size used by this encoder
        :return:
        """

        self.mVocabularySize = vocabularySize_
        self.mEncodedData = array('i')

    def encode(self, dataToEncode_, dataLen_, encodedData_, maxEncodedDataLen_):
        """
        Encode the data passed in. Just store the the symbols into the test integer array

        :param dataToEncode_: The data that needs to be compressed (integer array)
        :param dataLen_: The length of data that needs to be compressed
        :param encodedData_: Unused
        :param maxEncodedDataLen_ : Unused

        :return: The number of items stored in mEncodedData
        """

        # If the byte array is smaller than data length pass in throw exception
        if(len(dataToEncode_) < dataLen_):
            raise Exception("Data byte array passed in smaller than expected")

        # If the byte array is smaller than data length pass in throw exception
        if(len(encodedData_) < maxEncodedDataLen_):
            raise Exception("Compressed data byte array passed in smaller than expected")

        # Copy the data to the internal buffer
        for i in range(0, dataLen_):
            symbol = dataToEncode_[i]

            if(symbol >= self.mVocabularySize):
                raise Exception("Symbol out of bounds")

            self.mEncodedData.append(symbol)

        return dataLen_

    def reset(self):
        """
        This function does nothing

        :return:
        """

        pass




