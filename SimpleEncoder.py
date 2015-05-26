__author__ = 'Marko Milutinovic'

"""
This class is meant for testing. It implements a simple encoder that will simply store the passed in
data into array of integers. The base symbols are between 0-255 and they represent the actual data that is
being encoded. The base symbols can be extended when instantiating the object.
"""

from array import *

class SimpleEncoder:
    DEFAULT_VOCABULARY_SIZE = 256

    def __init__(self, numExtendedSymols_):
        """
        Initialize the symbol count based on default and extended character set. Initialize the integer array where
        data will be stored

        :param numExtendedSymols_: the number of additional symbols that will be added to vocabulary size
        :return:
        """

        self.mVocabularySize = self.DEFAULT_VOCABULARY_SIZE + numExtendedSymols_
        self.mEncodedData = array('i')
        self.mSymbolCount = 0

    def encode(self, symbol_):
        """
        Encode the symbol passed in. Just store the the symbol into the integer array

        :param symbol_: Symbol to be encoded
        :return: None
        """

        if(symbol_ >= self.mVocabularySize):
            raise Exception("Symbol out of bounds")

        self.mEncodedData.append(symbol_)
        self.mSymbolCount += 1

    def getEncodedData(self, outData_, maxOutDataLen_):
        """
        This function will not actually return any data as we are not encoding data. Just return 0 for the length of
        encoded data

        :param outData_: byte array where encoded data will be copied
        :param maxOutDataLen_: the max number of bytes that can be stored in outData_
        :return: the number of bytes that are stored in outData_
        """

        return self.mSymbolCount




