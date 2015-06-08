__author__ = 'Marko Milutinovic'

"""
This class implements a binary data compressor. The base vocabulary for the compressor will be 256 symbols, 0-255 and a termination symbol
whose value is 256. An Arithmetic Coding encoder will be used to encode the data into binary.

This code is designed as a proof of concept and has been designed with simplicity in mind. Efficiency is not a goal in
this implementation.

The compressor will go through five stages in order to compress the data.

The stages are as follows
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

        #Section size must be greater than 0
        if(sectionSize_ < 1):
            raise Exception('Section size must be greater than 0')

        self.mSectionSize = sectionSize_
        self.mSpecialSymbol1 = specialSymbol1_
        self.mSpecialSymbol1MaxRun = specialSymbol1MaxRun_
        self.mSpecialSymbol2 = specialSymbol2_
        self.mSpecialSymbol2MaxRun = specialSymbol2MaxRun_
        self.mGenericMaxRun = genericMaxRun_

        self.mVocabularySize = self.BASE_BINARY_VOCABULARY_SIZE + specialSymbol1MaxRun_ + specialSymbol2MaxRun_ + genericMaxRun_
        self.mBWTransforStoreBytes = utils.getMinBytesToRepresent(sectionSize_)
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

        runCount = 0
        outDataIndex = 0

        # Start with invalid symbol
        currentSymbol = self.INVALID_SYMBOL

        # If no data just return 0
        if(dataSize_ == 0):
            return 0

        # Go through all the data
        for i in range(0, dataSize_):

            # If the next symbol encountered is a repeat count increment the run count, otherwise process change
            if(currentSymbol == dataSection_[i]):
                runCount += 1
            else:
                #If this is not the first symbol encountered process any possible runs
                if(currentSymbol != self.INVALID_SYMBOL):

                    # Insert the previous symbol
                    dataSection_[outDataIndex] = currentSymbol
                    outDataIndex += 1

                    # If the run is greater than the max put in max run symbol
                    while(runCount > maxRunLength_):
                        dataSection_[outDataIndex] = runLengthSymbolStart_ + maxRunLength_ - 1
                        runCount -= maxRunLength_
                        outDataIndex += 1

                    # If the run is greater that or equal to 2, insert the replacement symbol. The first symbol indicates a run of 1 after the original symbol
                    if(runCount >= 2):
                        dataSection_[outDataIndex] = (runLengthSymbolStart_ + runCount - 1)
                        outDataIndex += 1

                runCount = 0
                currentSymbol = dataSection_[i]


        # Handle the last outstanding symbol
        dataSection_[outDataIndex] = currentSymbol
        outDataIndex += 1

        # If the run is greater than the max put in max run symbol
        while(runCount > maxRunLength_):
            dataSection_[outDataIndex] = runLengthSymbolStart_ + maxRunLength_ - 1
            runCount -= maxRunLength_
            outDataIndex += 1

        # If the run is greater that or equal to 2, insert the replacement symbol. The first symbol indicates a run of 1 after the original symbol
        if(runCount >= 2):
            dataSection_[outDataIndex] = (runLengthSymbolStart_ + runCount - 1)
            outDataIndex += 1

        return outDataIndex

    def _performBWTransform(self, dataSection_, dataSize):
        pass

    def kompress(self, inputData_, inputDataLen_, outputData_, maxOutputLen_):
        pass

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