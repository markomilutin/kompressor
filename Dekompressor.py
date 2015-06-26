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

        self.mWorkingArrayMaxSize = self.mSectionSize + self.mBWTransformStoreBytes
        self.mWorkingArray1 = array('i', [0]*(self.mWorkingArrayMaxSize))
        self.mWorkingArray2 = array('i', [0]*(self.mWorkingArrayMaxSize))

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

            # Ensure symbol is in allowed range, must be less than max vocabulary size
            if(currentSymbol > self.mVocabularySize):
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

            # Ensure symbol is in allowed range. Must be less than max vocabulary size
            if(currentSymbol > self.mVocabularySize):
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

        # Incoming data must be bigger than the transform information
        if(incomingDataSize_ <= self.mBWTransformStoreBytes):
            raise Exception('Not enough data')

        restoredDataIndex = 0

        # From the incoming data get the index of the original data sequence
        originalIndex = 0

        # Convert from little endian to number
        for i in range(0, self.mBWTransformStoreBytes):
            originalIndex |= ((incomingData_[i] & 0xFF) << (i*8))

        sortedData = array('i', sorted(incomingData_[self.mBWTransformStoreBytes:incomingDataSize_]))

        currentSymbol = 0xFFFF
        currentIndex = originalIndex

        # Set the number of required symbols to exclude the transform data
        numSymbolsToRevert = incomingDataSize_ - self.mBWTransformStoreBytes
        currentSymbol = sortedData[currentIndex]
        restoredData_[restoredDataIndex] = currentSymbol
        restoredDataIndex += 1
        numSymbolsToRevert -= 1

        # Go through all the data
        while(numSymbolsToRevert > 0):

            symbolCount = 1

            # Go through the sorted data and determine how many copies of the symbol appear beforehand
            for i in range(0,currentIndex):
                # If it's the same symbol increment count
                if(sortedData[i] == currentSymbol):
                    symbolCount += 1

            # Find the corresponding symbol in the transformed string, must be the at the same count as the symbol in the sorted array. Skip the indices with transform info which is not part of the original data
            currentIndex = self.mBWTransformStoreBytes

            # Go through the original sequence and find the matching symbol index which will be our next index in the sorted array
            while((currentIndex < incomingDataSize_) and (symbolCount > 0)):

                # If the current symbol has been found decrease the symbol count
                if(incomingData_[currentIndex] == currentSymbol):
                    symbolCount -= 1

                # If have not reached the symbol we want increment the index
                if(symbolCount != 0):
                    currentIndex += 1

            # We should always find the the symbols we are looking for
            if((currentIndex >= incomingDataSize_) or (symbolCount < 0)):
                raise Exception('Corrupted data')

            # Need to adjust as the transformed data contains extra transform info
            currentIndex -= self.mBWTransformStoreBytes

            # Get the current symbol and store it
            currentSymbol = sortedData[currentIndex]
            restoredData_[restoredDataIndex] = currentSymbol
            restoredDataIndex += 1
            numSymbolsToRevert -= 1

        return (incomingDataSize_ - self.mBWTransformStoreBytes)

    def dekompress(self, compressedData_, compressedDataLen_, outputData_, maxOutputDataLen_):
        """
        Pass in a byte array of data that has been compressed using Kompressor initialized with
        matching parameters. The uncompressed data will be stored in the outputData_ bytearray
        and the amount of data uncompressed will be returned.

        The max size that the compressedData can uncompress is limited by the data section size self.mSectionSize

        :param compressedData_: Compressed that needs to be uncompressed. Data must be passed in a bytearray
        :param compressedDataLen_: The size of compressed data
        :param outputData_: Uncompressed data will be stored here, this must  be a bytearray
        :param maxOutputDataLen_:  The max size of outputData_. If there is not enough room to store all the data an exception will be thrown
        :return: Number of bytes stored in outputData_
        """

        decodedDataLen_ = 0
        lengthAfterGenericExpansion = 0
        lengthAfterSymbol1Expansion = 0
        lengthAfterSymbol2Expansion = 0

        # Decode the data first
        decodedDataLen_ = self.mDecoder.decode(compressedData_, compressedDataLen_,self.mWorkingArray1, self.mWorkingArrayMaxSize)

        # Perform generic symbol run expansion
        lengthAfterGenericExpansion = self._expandRunsGeneric(self.mGenericRunLengthStart, self.mGenericMaxRun, self.mWorkingArray1, decodedDataLen_, self.mWorkingArray2, self.mWorkingArrayMaxSize)

        reverseTransformInputData = self.mWorkingArray2
        reverseTransformOutputData = self.mWorkingArray1
        lengthAfterSymbol2Expansion = lengthAfterGenericExpansion

        # Perform second character replacement if possible
        if(self.mSpecialSymbol2MaxRun > 1):
            lengthAfterSymbol2Expansion = self._expandRunsSpecific(self.mSpecialSymbol2, self.mSpecialSymbol2RunLengthStart, self.mSpecialSymbol2MaxRun, self.mWorkingArray2, lengthAfterGenericExpansion, self.mWorkingArray1, self.mWorkingArrayMaxSize)
            reverseTransformInputData = self.mWorkingArray1
            reverseTransformOutputData = self.mWorkingArray2

        # Reverse the BW transform
        lengthAfterBWReverse = self._reverseBWTransform(reverseTransformInputData, lengthAfterSymbol2Expansion, reverseTransformOutputData, self.mWorkingArrayMaxSize)

        finalOutputData = reverseTransformOutputData
        lengthAfterSymbol1Expansion = lengthAfterBWReverse

        # Perform first character expansion if possible
        if(self.mSpecialSymbol1MaxRun > 1):
            expandSymbol1InputData = reverseTransformOutputData
            expandSymbol1OutputData = reverseTransformInputData
            finalOutputData = expandSymbol1OutputData
            lengthAfterSymbol1Expansion = self._expandRunsSpecific(self.mSpecialSymbol1, self.mSpecialSymbol1RunLengthStart, self.mSpecialSymbol1MaxRun, expandSymbol1InputData, lengthAfterBWReverse, expandSymbol1OutputData, self.mWorkingArrayMaxSize)

        # If data exceeds section size throw exception
        if(lengthAfterSymbol1Expansion > self.mSectionSize):
            raise Exception('Data length exceeds max section size')

        # Ensure we have enough room to store all data
        if(lengthAfterSymbol1Expansion > maxOutputDataLen_):
            raise Exception('Not enough space to store uncompressed data')

        # Copy the data to the byte array, all data should be between 0-255
        for i in range(0, lengthAfterSymbol1Expansion):

            if(finalOutputData[i] > 255):
                raise Exception('Invalid symbol, not in byte range')

            outputData_[i] = finalOutputData[i]

        return lengthAfterSymbol1Expansion

    def reset(self):
        """
        Reset the decoder. Kompressor must be reset as wel otherwise we will not be able to decompress data
        :return:
        """
        self.mDecoder.reset()