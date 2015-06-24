__author__ = 'Marko Milutinovic'

"""
This class implements a binary data de-compressor. It is meant to be matched with a similarly configured Kompressor object.
The base vocabulary for the decompressor will be 256 symbols, 0-255 and a termination symbol whose value is 256. An Arithmetic
Coding decoder will be used to reconstruct data from binary.

This code is designed as a proof of concept and has been designed with simplicity in mind. Efficiency is not a goal in
this implementation.

The de-compressor will go through five stages in order to de-compress the data.

The stages are as follows:
    1. Decode data from binary into an array integer of symbols
    2. Expand symbols that indicate general runs into full symbol runs
    3. Expand symbols that indicate runs of special symbol #2
    4. Reverse the Burows-Wheeler transform
    5. Expand symbols that indicate runs of special symbol #1
"""

from array import *
from ARDecoder import ARDecoder
import utils

class Dekompressor:
    BASE_BINARY_VOCABULARY_SIZE = 257 # 0-255 for 8 bit characters plus termination symbol
    TERMINATION_SYMBOL = 256 # Used to indicate end of compression sequence
    INVALID_SYMBOL = 0xFFFF

    def __init__(self, sectionSize_, specialSymbol1_, specialSymbol1MaxRun_, specialSymbol2_, specialSymbol2MaxRun_, genericMaxRun_):
        """
        Constructor

        :param sectionSize_: Data section size to use to break up data when compressing
        :param specialSymbol1_: Special symbol whose runs will be removed before the BW transform
        :param specialSymbol1MaxRun_: The max run of special symbol 1
        :param specialSymbol2_: Special symbol whose runs will be removed after the BW transform
        :param specialSymbol2MaxRun_: The max run of special symbol 2
        :param genericMaxRun_: The max run of generic symbols
        :return:
        """

        # Section size must be greater than 0
        if(sectionSize_ < 1):
            raise Exception('Section size must be greater than 0')

        self.mSectionSize = sectionSize_
        self.mSpecialSymbol1 = specialSymbol1_
        self.mSpecialSymbol1MaxRun = specialSymbol1MaxRun_
        self.mSpecialSymbol1RunLengthStart = self.BASE_BINARY_VOCABULARY_SIZE
        self.mSpecialSymbol2 = specialSymbol2_
        self.mSpecialSymbol2MaxRun = specialSymbol2MaxRun_
        self.mSpecialSymbol2RunLengthStart = self.mSpecialSymbol1RunLengthStart + self.mSpecialSymbol1MaxRun
        self.mGenericMaxRun = genericMaxRun_
        self.mGenericRunLengthStart = self.mSpecialSymbol2RunLengthStart + self.mSpecialSymbol2MaxRun

        self.mVocabularySize = self.BASE_BINARY_VOCABULARY_SIZE + specialSymbol1MaxRun_ + specialSymbol2MaxRun_ + genericMaxRun_
        self.mBWTransformStoreBytes = utils.getMinBytesToRepresent(sectionSize_)
        self.mSectionTransformDataMaxSize = sectionSize_ + self.mBWTransformStoreBytes
        self.mSectionTransformData = array('i', [0]*(self.mSectionTransformDataMaxSize))
        self.mDecoder = ARDecoder(32, self.mVocabularySize, self.TERMINATION_SYMBOL)

        self.mContinuousModeEnabled = False
        self.mContinuousModeTotalData = 0
        self.mContinuousModeDataDecompressed = 0

    def _expandRunsSpecific(self, symbolToExpand, runLengthSymbolStart_, maxRunLength_, incomingData_ , incomingDataSize_, expandedData_, expandedDataMaxSize_):
        """
        Expand runs of symbol passed in based on extended symbols starting at runLengthSymbolStart_ and increases by
        upto maxRunLength. The data will be expanded

        :param symbolToExpand:
        :param runLengthSymbolStart_:
        :param maxRunLength_:
        :param dataSection:
        :param dataSize_:
        :return:
        """
        pass