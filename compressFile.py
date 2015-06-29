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
    outputOriginalInBinaryName = '3.104R1_BDG.dld.bin'
    outputCompressedFileName = '3.104R1_BDG.dld.compressed'

    totalCompressionTime = 0

    fileSize = 0
    compressedFileSize = 0

    inputData = array.array('i', [0]*2048)
    inputDataSize = 0

    kompressor = Kompressor(2048, 0x00, 5, 0x00, 0, 20)
    dekompressor = Dekompressor(2048, 0x00, 5, 0x00, 0, 20)

    # Hold all the compressed data in lines
    compressedFileData = []


    #outputOriginalInBinary = open(outputOriginalInBinaryName, 'wb+')
    #outputCompressedFile = open(outputCompressedFileName, 'wb+')

    # Go through each line in file
    with open(inputFileName, 'r+') as f, open(outputOriginalInBinaryName, 'wb+') as outputOriginalInBinary, open(outputCompressedFileName, 'wb+') as outputCompressedFile:

        for line in f:
            # Strip terminating characters and conver to hex from ascii

            line = line.strip()
            lineBytes = bytearray.fromhex(line)

            outputOriginalInBinary.write(lineBytes)
            inputDataSize = len(lineBytes)


            # Copy the data into the integer array
            for i in range(0, inputDataSize):
                inputData[i] = lineBytes[i]

            compressedData = bytearray(2048)
            compressedLineLen = kompressor.kompress(inputData, inputDataSize, compressedData, 2048,lastDataBlock=False)

            compressedFileData.append([compressedLineLen, inputDataSize, compressedData])

            #Write compressed line to compressed file
            outputCompressedFile.write(compressedData[0:compressedLineLen])

            fileSize += inputDataSize
            compressedFileSize += compressedLineLen


    #print('Filename: ' + inputFileName);
    #print('Size: ' + str(len(contents)))

    #profile = cProfile.Profile()
    #profile.enable()
    #testcode
    #profile.disable()

    decompressedFileData = []
    decompressedSize = 0

    # Dekompress the data stored in memory
    for i in range(0,len(compressedFileData)):
        decompressedData = bytearray(2048)
        [compressedLineLen, inputDataSize, compressedLineData]  = compressedFileData[i]

        decompressedDataLen = dekompressor.dekompress(compressedLineData, compressedLineLen, decompressedData, 2048)

        if(decompressedDataLen != inputDataSize):
            print('ERROR decompressing 1 at line [' + str(i) + ']')
            #exit(0)

        decompressedSize += decompressedDataLen
        decompressedFileData.append([decompressedDataLen, decompressedData])

    #Go through and veriy all decompressed lines match original
    count = 0
    with open(inputFileName, 'r+') as f:

        for line in f:
            # Strip terminating characters and conver to hex from ascii
            line = line.strip()
            lineBytes = bytearray.fromhex(line)

            if(decompressedFileData[count][0] != len(lineBytes) or decompressedFileData[count][1][:decompressedFileData[count][0]] != lineBytes):
                print('ERROR decompressing on line [' + str(count) + ']\r\n')
                exit(0)

            count += 1

    print('Compressed Size: ', str(compressedFileSize))
    print('Compression Percentage: ', str(compressedFileSize/fileSize))

    print('\n\n')
    #profile.print_stats()

if __name__ == "__main__":
    main()