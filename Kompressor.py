__author__ = 'Marko Milutinovic'

"""
This class implements a binary data compressor. The base vocabulary for the compressor will be 256 symbols, 0-255 and a termination symbol
whose value is 256. An Arithmetic Coding encoder will be used to encode the data into binary.

This code is designed as a proof of concept and has been designed with simplicity in mind. Efficiency is not a goal in
this implementation.

The compressor will go through five stages in order to compress the data.

The stages are as follows:
    1. The Burrows-Wheeler transform will be performed on the data. This stage will maximize the runs of symbols
    2. Replace runs of symbols with initial symbol and extra symbol indicating length of run. Extended symbols will be
       added to support this.
    3. Encoded data into binary using an encoder
"""

from array import *
from AREncoder import AREncoder
import utils

dataSorting = None
dataSortingSize = 0

# This class is used to sort data for the BW transform
class SortKey:
    def __init__(self, keyData_, *args):
        self.mIndex = keyData_[0]
        self.mData = keyData_[1]
        self.mDataSize = keyData_[2]

    def __lt__(self, rightKey_):
        for i in range(0, self.mDataSize):
            leftData = self.mData[(i+self.mIndex)%self.mDataSize]
            rightData = self.mData[(i+rightKey_.mIndex)%self.mDataSize]

            if(leftData < rightData):
                return True
            elif(leftData > rightData):
                return False

        return False

    def __gt__(self, rightPermutationIndex_):
        return False

    def __eq__(self, rightPermutationIndex_):
        return False

    def __le__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __ne__(self, other):
        return False


class Kompressor:
    BASE_BINARY_VOCABULARY_SIZE = 257 # 0-255 for 8-bit characters plus termination symbol
    TERMINATION_SYMBOL = 256 # Used to indicate end of compression sequence
    INVALID_SYMBOL = 0xFFFF

    def __init__(self, sectionSize_, genericMaxRun_, encoderWordSize_ = 16):
        """
        Constructor

        :param sectionSize_: Data section size to use to break up data when compressing
        :param genericMaxRun_: The max run of generic symbols
        :param encoderWordSize_: The size of words (in bits) to use for encoding data
        :return:
        """

        # Section size must be greater than 0
        if(sectionSize_ < 1):
            raise Exception('Section size must be greater than 0')

        # Ensure that generic max run is at least one
        if(genericMaxRun_ < 1):
            genericMaxRun_ = 1

        self.mSectionSize = sectionSize_
        self.mGenericMaxRun = genericMaxRun_
        self.mGenericRunLengthStart = self.BASE_BINARY_VOCABULARY_SIZE

        self.mVocabularySize = self.BASE_BINARY_VOCABULARY_SIZE + genericMaxRun_
        self.mBWTransformStoreBytes = utils.getMinBytesToRepresent(sectionSize_)
        self.mSectionTransformDataMaxSize = sectionSize_ + self.mBWTransformStoreBytes
        self.mSectionTransformData = array('i', [0]*(self.mSectionTransformDataMaxSize))
        self.mEncoder = AREncoder(encoderWordSize_, self.mVocabularySize)

        self.mContinuousModeEnabled = False
        self.mContinuousModeTotalData = 0
        self.mContinuousModeDataCompressed = 0

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

        #TODO: need test for this case
        # If the run is greater than the max put in max run symbol. Run count includes original symbol
        while(duplicateCount > maxDuplicateCount):
            dataSection_[outDataIndex] = runLengthSymbolStart_ + maxDuplicateCount - 1
            duplicateCount -= maxDuplicateCount
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

        #K = SortKey(dataSection_, dataSize_)
        sortData = []
        for i in range(0, dataSize_):
            sortData.append([i, dataSection_, dataSize_])

        indecesOfDataPermutations = sorted(sortData, key=SortKey)

        #Find the original data sequence in the sorted indecesOfDataPermutations
        originalSequenceIndex = indecesOfDataPermutations.index([0, dataSection_, dataSize_])

        # Add the original sequence index at the front of the transform (split into bytes, little endian)
        for i in range(0, self.mBWTransformStoreBytes):
            transformedData_[i] = ((originalSequenceIndex >> (i*8)) & 0xFF)

        for i in range(self.mBWTransformStoreBytes, dataSize_ + self.mBWTransformStoreBytes):
            transformedData_[i] = dataSection_[(dataSize_ - 1 + indecesOfDataPermutations[i-self.mBWTransformStoreBytes][0])%dataSize_]

        return (dataSize_ + self.mBWTransformStoreBytes)

    def kompress(self, inputData_, inputDataLen_, outputData_, maxOutputLen_, lastDataBlock=True):
        """
        Pass in integer array of data that needs to be compressed. The compressed data will
        be stored in the outputData_ bytearray.

        :param inputData_: bytearray that holds the data that needs to be compressed. Data will be modified during compression sequence
        :param inputDataLen_: The data size must be less than or equal to self.mSectionSize
        :param outputData_: Byte array that will hold the compressed binary data
        :param maxOutputLen_: The maximum size of the outputData_ array. If this is not enough to store compressed data an exception will be thrown
        :return: Return the size of the compressed data in outputData_
        """

        lengthAfterSymbol1Replacement = 0
        lengthAfterSymbol2Replacement = 0
        lengthAfterBWTransform = 0
        lengthAfterGenericReplacement = 0

        # If data exceeds section size throw exception
        if(inputDataLen_ > self.mSectionSize):
            raise Exception('Data length exceeds max section size')

        # Transform data using BW transform
        lengthAfterBWTransform = self._performBWTransform(inputData_, inputDataLen_, self.mSectionTransformData, self.mSectionTransformDataMaxSize)

        # Perform generic symbol run replacement
        lengthAfterGenericReplacement = self._replaceRunsGeneric(self.mGenericRunLengthStart, self.mGenericMaxRun, self.mSectionTransformData, lengthAfterBWTransform)

        # Encode the data
        self.mSectionTransformData[lengthAfterGenericReplacement] = self.TERMINATION_SYMBOL
        lengthAfterGenericReplacement += 1

        return self.mEncoder.encode(self.mSectionTransformData, lengthAfterGenericReplacement, outputData_, maxOutputLen_, lastDataBlock=lastDataBlock)

    def reset(self):
        """
        Reset the encoder. This will reset all encoder statistics. Dekompressor must be reset as well otherwise we will not be able to decompress data

        :return:
        """
        self.mEncoder.reset()