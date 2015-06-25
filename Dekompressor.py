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
        upto maxRunLength. The data will be expanded in to the expandedData_ array up to expandedDataMaxSize_

        :param symbolToExpand: The symbol that will be expanded based on the extended symbols
        :param runLengthSymbolStart_: The first extended symbol that indicates a run of the symbol passed in
        :param maxRunLength_: The max run length which indicates the last extended symbol that we can expect
        :param incomingData_: The incoming data that we are expanding (integer array)
        :param incomingDataSize_: The size of the incoming data
        :param expandedData_: Expanded data will be stored here (integer array)
        :param expandedDataMaxSize_: The max number of symbols that can be stored in expandedData_
        :return: Return the number of symbols stored in expandedData_
        """

        currentIncomingDataIndex = 0
        currentExpandedDataIndex = 0
        currentSymbol = 0xFFFF

        # Go through all the incoming data
        while(currentIncomingDataIndex < incomingDataSize_):

            currentSymbol = incomingData_[currentIncomingDataIndex]
            currentIncomingDataIndex += 1

            # Ensure symbol is in allowed range. Must be between 0-256 or (runLengthSymbolStart_) to (runLengthSymbolStart_ + (maxRunLength - 2))
            if(((currentSymbol > 255) and (currentSymbol < runLengthSymbolStart_)) or
               (currentSymbol > (runLengthSymbolStart_ + maxRunLength_))):
                raise Exception('Symbol [' + str(currentSymbol) + '] out of range')

            # If binary value copy else if this is an extended symbol then expand out the symbol provided. Note the first extended symbol represents a run of two so need to offset by two
            if(currentSymbol >= runLengthSymbolStart_):

                # The run length is based on the current extended symbol. Find the offset from the base extended symbol and add 2 to reflect that the base represents a run of two
                runLength = currentSymbol - runLengthSymbolStart_ + 2

                # If there is not enough room to to store the expanded data throw exception
                if((currentExpandedDataIndex + runLength) >= expandedDataMaxSize_):
                    raise Exception('Not enough space in expansion array 1')

                # Insert the run into the expanded data
                for i in range(0, runLength):
                    expandedData_[currentExpandedDataIndex] = symbolToExpand
                    currentExpandedDataIndex += 1
            else:
                # If there is not enough data to store the next symbol throw exception
                if((currentExpandedDataIndex + 1) >= expandedDataMaxSize_):
                    raise Exception('Not enough space in expansion array 2')

                expandedData_[currentExpandedDataIndex] = currentSymbol
                currentExpandedDataIndex +=1

        return currentExpandedDataIndex


    def _expandRunsGeneric(self, runLengthSymbolStart_, maxRunLength_, incomingData_, incomingDataSize_, expandedData_, expandedDataMaxSize_):
        """
        Expand extended symbols that indicate runs of generic symbols.

        :param runLengthSymbolStart_: First extended symbol that is used to indicate how many times the original symbol is repeated. First symbol indicates a repeat of one
        :param maxRunLength_: The max size of a run that can be replaced
        :param incomingData_: The data that needs to be expanded (integer array)
        :param incomingDataSize_: The size of the incoming array
        :param expandedData_: The expanded data will be stored here (integer array)
        :param maxExpandedDataSize: The max number of symbols that the expanded data can be. An exception will be thrown if exceeded
        :return: The number of symbols stored in expandedData_
        """

        currentIncomingDataIndex = 0
        currentExpandedDataIndex = 0
        currentSymbol = 0xFFFF
        previousSymbol = 0xFFFF

        if(incomingDataSize_ == 0 ):
            return 0

        currentSymbol = incomingData_[currentIncomingDataIndex]
        currentIncomingDataIndex += 1

        # The first symbol must be a number between 0-255
        if(currentSymbol > 255):
            raise Exception('Invalid first symbol')

        # Store the first symbol
        expandedData_[currentExpandedDataIndex] = currentSymbol
        currentExpandedDataIndex += 1
        previousSymbol = currentSymbol

        # Go through all the incoming data
        while(currentIncomingDataIndex < incomingDataSize_):

            currentSymbol = incomingData_[currentIncomingDataIndex]
            currentIncomingDataIndex += 1

            # Ensure symbol is in allowed range. Must be between 0-256 or (runLengthSymbolStart_) to (runLengthSymbolStart_ + (maxRunLength - 2))
            if(((currentSymbol > 255) and (currentSymbol < runLengthSymbolStart_)) or
               (currentSymbol > (runLengthSymbolStart_ + maxRunLength_))):
                raise Exception('Symbol [' + str(currentSymbol) + '] out of range')

            # If byte value copy else if this is an extended symbol then expand out the previous symbol provided. Note the first extended symbol represents a run of 1 so need to offset by one
            if(currentSymbol >= runLengthSymbolStart_):

                # The run length is based on the current extended symbol. Find the offset from the base extended symbol and add 1 to reflect that the base represents a run of one
                runLength = currentSymbol - runLengthSymbolStart_ + 1

                # If there is not enough room to to store the expanded data throw exception
                if((currentExpandedDataIndex + runLength) >= expandedDataMaxSize_):
                    raise Exception('Not enough space in expansion array 1')

                for i in range(0, runLength):
                    expandedData_[currentExpandedDataIndex] = previousSymbol
                    currentExpandedDataIndex += 1
            else:
                # If there is not enough room to to store the symbol throw exception
                if((currentExpandedDataIndex + 1) >= expandedDataMaxSize_):
                    raise Exception('Not enough space in expansion array 2')

                expandedData_[currentExpandedDataIndex] = currentSymbol
                currentExpandedDataIndex +=1

                # Only update the previous symbol on a non extended character, as multiple extended symbols could be representing a long run of a symbol
                previousSymbol = currentSymbol

        return currentExpandedDataIndex

    def _reverseBWTransform(self, incomingData_, incomingDataSize_, restoredData_, restoredDataMaxLen_):
        """
        Reverse BW transform on incomingData_. This will revert the data to it's pre transform state.
        The reversed data will be stored in restoredData_

        :param incomingData_: The data to be reverted which is an array
        :param incomingDataSize_: The length of the data to be reverted
        :param restoredData_: The reversed data will be stored here. This is an array
        :param restoredDataMaxLen_: The max length of restoredData_
        :return: The size of the reverted data
        """

        # From the incoming data get the index of the original data sequence
        originalIndex = 0

        # Convert from little endian to number
        for i in range(0, self.mBWTransformStoreBytes):
            originalIndex |= ((incomingData_[i] & 0xFF) << (i*8))

        sortedData = array('i', sorted(incomingData_[self.mBWTransformStoreBytes:]))

        currentSymbol = 0xFFFF
        currentIndex =
        numSymbolsToRevert = incomingDataSize_ - self.mBWTransformStoreBytes

        while(numSymbolsToRevert > 0):
            #

        return (incomingDataSize_ - self.mBWTransformStoreBytes)


