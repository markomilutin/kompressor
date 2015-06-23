__author__ = 'Marko Milutinovic'

"""
This class implements a binary data compressor. The base vocabulary for the compressor will be 256 symbols, 0-255 and a termination symbol
whose value is 256. An Arithmetic Coding encoder will be used to encode the data into binary.

This code is designed as a proof of concept and has been designed with simplicity in mind. Efficiency is not a goal in
this implementation.

The compressor will go through five stages in order to compress the data.

The stages are as follows:
    1. If defined, replaces runs (2 - defined) of special symbol #1 by extended symbols. Extended symbols will be added
       to support replacing runs of data.
    2. The Burrows-Wheeler transform will be performed on the data. This stage will maximize the runs of symbols
    3. If defined, replaces runs (2 - defined) of special symbol #2 by extended symbols. Extended symbols will be added
       to support replacing runs of data.
    4. Replace runs of symbols with initial symbol and extra symbol indicating length of run. Extended symbols will be
       added to support this. This stage will replace runs of all symbols.
    5. Encoded data into binary using an encoder
"""

from array import *
from AREncoder import AREncoder
import utils

class Kompressor:
    BASE_BINARY_VOCABULARY_SIZE = 257 # 0-255 for 8-bit characters plus termination symbol
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
        self.mEncoder = AREncoder(32, self.mVocabularySize)

        self.mContinuousModeEnabled = False
        self.mContinuousModeTotalData = 0
        self.mContinuousModeDataCompressed = 0

    def _replaceRunsSpecific(self, symbolToReplace_, runLengthSymbolStart_, maxRunLength_, dataSection_, dataSize_):
        """
        Remove runs of symbol passed in using extended symbols that start at runLengthSymbolStart_. Run length is defined
        by maxRunLength_. The data will be stored in place in dataSection_ array provided array. The new length of dataSection
        will be returned

        :param symbolToReplace_: The symbol whose runs we are replacing
        :param runLengthSymbolStart_: The start symbol of symbols used to replace runs of data. First symbol indicates run of two
        :param maxRunLength_: The maximum run length we will be replacing
        :param dataSection_: The data section on which we are working. This is an array
        :param dataSize_: The size of the array
        :return: The new size of the dataSection_ array after replacement is finished
        """
        runCount = 0
        outDataIndex = 0

        # Go through all the data
        for i in range(0, dataSize_):

            # If the next symbol encountered is the symbol we are replacing just increment the run count, otherwise process change
            if(symbolToReplace_ == dataSection_[i]):
                runCount += 1
            else:
                # If the run is greater than the max put in max symbol
                while(runCount > maxRunLength_):
                    dataSection_[outDataIndex] = runLengthSymbolStart_ + maxRunLength_ - 2
                    runCount -= maxRunLength_
                    outDataIndex += 1

                # If the run is greater that or equal to 2, insert the replacement symbol. The first symbol indicates a run of two. If it is a run of 1 then put the symbol back in
                if(runCount >= 2):
                    dataSection_[outDataIndex] = (runLengthSymbolStart_ + runCount - 2)
                    outDataIndex += 1
                elif(runCount == 1):
                    dataSection_[outDataIndex] = symbolToReplace_
                    outDataIndex += 1

                runCount = 0

                # Insert the symbol that was just encountered
                dataSection_[outDataIndex] = dataSection_[i]
                outDataIndex += 1

        # If there is a run collected at the end, replace with appropriate symbol(s).
        while(runCount > maxRunLength_):
            dataSection_[outDataIndex] = runLengthSymbolStart_ + maxRunLength_ - 2
            runCount -= maxRunLength_
            outDataIndex += 1

        # If the run is greater that or equal to 2, insert the replacement symbol. The first symbol indicates a run of two. If it is a run of 1 then put the symbol back in
        if(runCount >= 2):
            dataSection_[outDataIndex] = (runLengthSymbolStart_ + runCount - 2)
            outDataIndex += 1
        elif(runCount == 1):
            dataSection_[outDataIndex] = symbolToReplace_
            outDataIndex += 1

        return outDataIndex

    def _replaceRunsGeneric(self, runLengthSymbolStart_, maxRunLength_, dataSection_, dataSize_):
        """
        Replace runs of symbols with generic symbol replacements. A run greater or equal to two symbols should be replaced
        with the first symbol in the run and an extended symbol to indicate how many times it's repeated.

        :param runLengthSymbolStart_: First extended symbol that is used to indicate how many times the original symbol is repeated. First symbol indicates a repeat of one
        :param maxRunLength_: The max size of a run that can be replaced
        :param dataSection_: The data section on which we are working. This is an array
        :param dataSize_: The size of the array
        :return: The new size of the dataSection_ array after replacement is finished
        """
        maxDuplicateCount = maxRunLength_ - 1
        duplicateCount = 0
        outDataIndex = 0

        # Start with invalid symbol
        currentSymbol = self.INVALID_SYMBOL

        # If no data just return 0
        if((dataSize_ == 0) or (maxRunLength_ <= 1)):
            return dataSize_

        # Go through all the data
        for i in range(0, dataSize_):
            # If the next symbol encountered is a repeat increment the duplicate count, otherwise process change
            if(currentSymbol == dataSection_[i]):
                duplicateCount += 1
            else:
                #If this is not the first symbol encountered process any possible runs
                if(currentSymbol != self.INVALID_SYMBOL):

                    # Insert the previous symbol
                    dataSection_[outDataIndex] = currentSymbol
                    outDataIndex += 1

                    # If the run is greater than the max put in max run symbol.
                    while(duplicateCount > maxDuplicateCount):
                        dataSection_[outDataIndex] = runLengthSymbolStart_ + maxDuplicateCount - 1
                        duplicateCount -= maxDuplicateCount
                        outDataIndex += 1

                    # If the run is greater that or equal to 1, insert the replacement symbol. Run count does not include original symbol
                    if(duplicateCount >= 1):
                        dataSection_[outDataIndex] = (runLengthSymbolStart_ + duplicateCount - 1)
                        outDataIndex += 1

                duplicateCount = 0
                currentSymbol = dataSection_[i]

        # Handle the last outstanding symbol
        dataSection_[outDataIndex] = currentSymbol
        outDataIndex += 1

        # If the run is greater than the max put in max run symbol. Run count includes original symbol
        while(duplicateCount > maxDuplicateCount):
            dataSection_[outDataIndex] = runLengthSymbolStart_ + maxDuplicateCount - 1
            duplicateCount -= maxRunLength_
            outDataIndex += 1

        # If the run is greater that or equal to 1, insert the replacement symbol
        if(duplicateCount >= 1):
            dataSection_[outDataIndex] = (runLengthSymbolStart_ + duplicateCount - 1)
            outDataIndex += 1

        return outDataIndex

    def _bytearrayLessThan(self, originalData_, leftPermutationIndex_, rightPermutationIndex_, len_):
        """
        Determine which byte array is less based on data sorted in lexigraphical order. Use the permutation indeces and the original
        data to construct byte arrays that are being compared. If left is smaller return -1, if right is smaller return 1
        and if they are the same return 0

        :param originalData_: The original byte array
        :param leftData_: Permutation index of left side. This is a permutation index which will be used to construct the byte array from the original data
        :param rightData_: Permutation index of right side. This is a permutation index which will be used to construct the byte array from the original data
        :param len_: Length of left and right byte arrays (NOTE: they must be the same length)

        :return: -1 ir leftData < rightdata, 1 if rightData < leftData, 0 if rightData == leftData
        """
        for i in range(0, len_):
            leftData = originalData_[(i+leftPermutationIndex_)%len_]
            rightData = originalData_[(i+rightPermutationIndex_)%len_]
            if(leftData < rightData):
                return -1
            elif(leftData > rightData):
                return 1

        return 0

    def _performBWTransform(self, dataSection_, dataSize_, transformedData_, transformedDataMaxLen_):
        """ Perform BW transform on dataSection_. This transform will maximize the chances of equal bytes being grouped
            together. The result will be stored in transformedData_

        :param dataSection_: The data to be transformed which is an array
        :param dataSize_: The length of the data to be transformed
        :param transformedData_: The transformed data will be stored here. There must be at least inLen_ + self.mBWTransformStoreBytes bytes available. This is an array
        :param transformedDataLen_: The length of outputData_. Must be at least inLen_ + self.mBWTransformStoreBytes bytes
        :return: The size of the transformed data
        """

        if(transformedDataMaxLen_ < (dataSize_ + self.mBWTransformStoreBytes)):
            raise Exception("Output data array to small")

        # The full array is the first boundary
        stack = [(0, dataSize_)]

        # Start with permutations of original data ordered 0 to dataSize_. This will be sorted according the contents of the permutations
        indecesOfDataPermutations = bytearray(dataSize_)

        # Set the indeces based on permutation
        for i in range(0, dataSize_):
            indecesOfDataPermutations[i] = i

        # Perform QuickSort of indices based on the contents of data permutations
        while len(stack) > 0:
            bounds = stack.pop()
            pivotIndex = int((bounds[0] + bounds[1])/2)

            pivot = indecesOfDataPermutations[pivotIndex]

            # Move the pivot to the top of the range
            temp = indecesOfDataPermutations[bounds[1]-1]
            indecesOfDataPermutations[bounds[1]-1] = pivot
            indecesOfDataPermutations[pivotIndex] = temp

            storeIndex = bounds[0]

            #Compare remaining indeces against pivot value
            for i in range(bounds[0], bounds[1]):
                #If permutation is less than pivot swap place with the current value at the store index
                if(self._bytearrayLessThan(dataSection_, indecesOfDataPermutations[i], pivot, dataSize_) == -1):
                    temp = indecesOfDataPermutations[storeIndex]
                    indecesOfDataPermutations[storeIndex] = indecesOfDataPermutations[i]
                    indecesOfDataPermutations[i] = temp
                    storeIndex += 1

            #Place pivot at it's correct location
            temp = indecesOfDataPermutations[storeIndex]
            indecesOfDataPermutations[storeIndex] = indecesOfDataPermutations[bounds[1] - 1]
            indecesOfDataPermutations[bounds[1] - 1] = temp

            #If we can keep sub dividing, do so
            if(bounds[0] < storeIndex):
                stack.append((bounds[0], storeIndex))

            if(storeIndex < (bounds[1]-1)):
                stack.append((storeIndex + 1, bounds[1]))

        #Find the original data sequence in the sorted indecesOfDataPermutations
        originalSequenceIndex = indecesOfDataPermutations.find(0)

        # Add the original sequence index at the front of the transform (split into bytes, little endian)
        for i in range(0, self.mBWTransformStoreBytes):
            transformedData_[i] = ((originalSequenceIndex >> (i*8)) & 0xFF)

        for i in range(self.mBWTransformStoreBytes, dataSize_ + self.mBWTransformStoreBytes):
            transformedData_[i] = dataSection_[(dataSize_ - 1 + indecesOfDataPermutations[i-self.mBWTransformStoreBytes])%dataSize_]

        return (dataSize_ + self.mBWTransformStoreBytes)

    def kompress(self, inputData_, inputDataLen_, outputData_, maxOutputLen_):
        """
        Pass in integer array of data that needs to be compressed. The compressed data will
        be stored in the outputData_ bytearray.

        :param inputData_: Array that holds the data that needs to be compressed
        :param inputDataLen_: The data size must be less than or equal to self.mSectionSize
        :param outputData_: Byte array that will hold the compressed binary data
        :param maxOutputLen_: The maximum size of the outputData_ array. If this is not enough to store compressed data an exception will be thrown
        :return: Return the size of the compressed data in outputData_
        """

        # If data exceeds section size throw exception
        if(inputDataLen_ > self.mSectionSize):
            raise Exception('Data length exceeds max section size')

        # Perform first character replacement if possible
        if(self.mSpecialSymbol1MaxRun > 1):
            inputDataLen_ = self._replaceRunsSpecific(self.mSpecialSymbol1, self.mSpecialSymbol1RunLengthStart, self.mSpecialSymbol1MaxRun, inputData_, inputDataLen_)

        # Transform data using BW transform
        transformedDataLen = self._performBWTransform(inputData_, inputDataLen_, self.mSectionTransformData, self.mSectionTransformDataMaxSize)

        # Perform second character replacement if possible
        if(self.mSpecialSymbol2MaxRun > 1):
            transformedDataLen = self._replaceRunsSpecific(self.mSpecialSymbol2, self.mSpecialSymbol2RunLengthStart, self.mSpecialSymbol2MaxRun, self.mSectionTransformData, transformedDataLen)

        # Perform generic symbol run replacement
        transformedDataLen = self._replaceRunsGeneric(self.mGenericRunLengthStart, self.mGenericMaxRun, self.mSectionTransformData, transformedDataLen)

        # Encode the data
        self.mSectionTransformData[transformedDataLen] = self.TERMINATION_SYMBOL
        transformedDataLen += 1

        return self.mEncoder.encode(self.mSectionTransformData, transformedDataLen, outputData_, maxOutputLen_)

    def kompressStartContinuous(self, totalDataToCompress_):
        """
        Enable continuous compression mode. The totalDataToCompress_ size will determine how long this mode will run
        without resetting the encoder

        :param totalDataToCompress_: The duration of the continuous mode
        :return:
        """
        pass

    def kompressStopContinuous(self):
        """
        Stops the continuous compressions mode if its currently running.

        :return:
        """

    def kompressFeedContinuous(self, inputData_, inputDataLen_, outputData_, outputDataOffset_, maxOutputLen_):
        """

        :param inputData_:
        :param inputDataLen_:
        :param outputData_:
        :param outputDataOffset_:
        :param maxOutputLen_:
        :return: True if continuous mode is still running. If we have satisfied the total data requirement, stop continuous mode and return False
        """