__author__ = 'Marko Milutinovic'

"""
This class implements a binary data compressor. The base vocabulary for the compressor will be 256 symbols, 0-255 and a termination symbol
whose value is 256. An Arithmetic Coding encoder will be used to encode the data into binary.

The compressor will Ago through three stages in order to compress the data.

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
