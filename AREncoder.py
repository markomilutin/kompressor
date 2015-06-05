__author__ = 'Marko Milutinovic'

"""
This class will implement an Arithmetic Coding encoder
"""

class AREncoder:
    def __init__(self, wordSize_, vocabularySize_):
        """

        :param wordSize_: The word size (bits) that will be used for encoding. Must be greater than 2 and less than or equal to 32
        :param vocabularySize_: The size of the vocabulary. Symbols run from 0 to (vocabularySize_ - 1)
        :return:
        """
        pass

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


