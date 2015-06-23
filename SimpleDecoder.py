__author__ = 'Marko Milutinovic'

"""
This class is meant for testing. It implements a simple decoder that will simply pass back data from a local
integer array. The symbols allowed run from 0 to the vocabulary size -1
"""

from array import *

class SimpleDecoder:
    def __init__(self, decodedData_, decodedDataLen_):
        """
        Set the array which will be used to send information back on a decode

        :param decodedData_: Data that will be sent back on a secode
        :param decodedDataLen_: The length of the decoded data
        :return:
        """

        self.mDecodedData = decodedData_
        self.mDecodedDataLen = decodedDataLen_

    def decode(self, encodedData_, dataLen_, decodedData_, maxDecodedDataLen_):
        """
        Will return preset array of decoded data. If decodedData_ does not have the space to store all data an exception
        will be thrown

        :param encodedData_: Incoming data that needs to be decoded (bytearray)
        :param dataLen_:  The length of the incoming encoded data
        :param decodedData_: The decoded data will be copied to this integer array
        :param maxDecodedDataLen_: The max number of symbols that can be stored in decodedData_
        :return: The number of symbols stored in decodedData_
        """

        # If the byte array is smaller than data length pass in throw exception
        if(len(encodedData_) < dataLen_):
            raise Exception("Data byte array passed in smaller than expected")

        # If the byte array is smaller than data length pass in throw exception
        if(len(decodedData_) < maxDecodedDataLen_):
            raise Exception("Outgoing data array passed in smaller than expected")

        if(self.mDecodedDataLen > maxDecodedDataLen_):
            raise Exception("Not enough space to store decoded data")

        # Copy all the stored data as outgoing data
        for i in range(0, self.mDecodedDataLen):
            decodedData_[i] = self.mDecodedData

        return self.mDecodedDataLen

    def reset(self):
        """
        Does nothing

        :return:
        """