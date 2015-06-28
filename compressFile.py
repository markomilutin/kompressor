__author__ = 'marko'

import sys
from Kompressor import Kompressor
from Dekompressor import Dekompressor
import cProfile
import os
import array
from binascii import unhexlify

def main():
    #inputFileName = sys.argv[1]

    inputFileName = '3.104R1_BDG.dld'
    outputOriginalInBinary = '3.104R1_BDG.dld.bin'

    fileSize = 0
    compressedFileSize = 0

    inputData = array.array('i', [0]*2048)
    inputDataSize = 0

    kompressor = Kompressor(2048, 0x00, 10, 0xFF, 0, 15)
    dekompressor = Dekompressor(2048, 0xFF, 3, 0xFF, 2, 10)

    # Hold all the compressed data in lines
    compressedFileData = []

    with open(outputOriginalInBinary, 'wb+') as outBinary:
        # Go through each line in file
        with open(inputFileName, 'r+') as f:

            for line in f:
                # Strip terminating characters and conver to hex from ascii

                line = line.strip()
                lineBytes = bytearray.fromhex(line)

                outBinary.write(lineBytes)
                inputDataSize = len(lineBytes)

                # Copy the data into the integer array
                for i in range(0, inputDataSize):
                    inputData[i] = lineBytes[i]


                compressedData = bytearray(2048)
                compressedLineLen = kompressor.kompress(inputData, inputDataSize, compressedData, 2048)

                compressedFileData.append([compressedLineLen, inputDataSize, compressedData])

                # Copy to integer array
                fileSize += inputDataSize
                compressedFileSize += compressedLineLen


    print('Filename: ' + inputFileName);
    #print('Size: ' + str(len(contents)))

    profile = cProfile.Profile()
    profile.enable()
    #compressedDataLen = compressor.compress_data(contents, len(contents), compressedData, len(contents)*2)
    profile.disable()

    print('Compressed Size: ', str(compressedDataLen))
    print('Compression Percentage: ', str(compressedDataLen/len(contents)))

    print('\n\n')
    profile.print_stats()

if __name__ == "__main__":
    main()