__author__ = 'Marko Milutinovic'

import unittest
from array import array

from Kompressor import Kompressor
from SimpleEncoder import SimpleEncoder

class KompressorTests(unittest.TestCase):
    def test_constructor(self):
        """
        Purpose: Instantiate an object
        Expectation: The member variables should be initialized correctly
        """

        kompressor = Kompressor(256, 0x00, 3, 0xFF, 4, 10)

        self.assertEqual(256, kompressor.mSectionSize)
        self.assertEqual(0, kompressor.mSpecialSymbol1)
        self.assertEqual(3, kompressor.mSpecialSymbol1MaxRun)
        self.assertEqual(257, kompressor.mSpecialSymbol1RunLengthStart)
        self.assertEqual(0xFF, kompressor.mSpecialSymbol2)
        self.assertEqual(4, kompressor.mSpecialSymbol2MaxRun)
        self.assertEqual(260, kompressor.mSpecialSymbol2RunLengthStart)
        self.assertEqual(10, kompressor.mGenericMaxRun)
        self.assertEqual(264, kompressor.mGenericRunLengthStart)
        self.assertEqual(257+3+4+10, kompressor.mVocabularySize)
        self.assertEqual(1, kompressor.mBWTransformStoreBytes)
        self.assertNotEqual(None, kompressor.mSectionTransformData)
        self.assertEqual(257, len(kompressor.mSectionTransformData))
        self.assertEqual(257, kompressor.mSectionTransformDataMaxSize)
        self.assertNotEqual(None, kompressor.mEncoder)
        self.assertEqual(False, kompressor.mContinuousModeEnabled)
        self.assertEqual(0, kompressor.mContinuousModeTotalData)
        self.assertEqual(0, kompressor.mContinuousModeDataCompressed)

    def test_replaceRunsSpecific_no_symbols(self):
        """
        Purpose: Pass in data that has no data
        Expectation: 0 should be returned
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [])

        newLength = kompressor._replaceRunsSpecific(55, 257, 10, data, 0)

        self.assertEqual(0, newLength)

    def test_replaceRunsSpecific_one_symbol_special(self):
        """
        Purpose: Pass in data that has no data
        Expectation: 0 should be returned
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [])

        newLength = kompressor._replaceRunsSpecific(55, 257, 10, data, 0)

        self.assertEqual(0, newLength)

    def test_replaceRunsSpecific_no_runs_nosymbol(self):
        """
        Purpose: Pass in data that has no runs of the specified symbol but has runs of other symbols. The symbol we are replacing is not in the data either
        Expectation: The data should be unchanged as there are no runs to replace
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [0, 0, 1, 1, 2, 2, 3, 4, 6, 7, 8, 9, 11, 12, 23])

        newLength = kompressor._replaceRunsSpecific(55, 257, 10, data, 15)

        self.assertEqual(15, newLength)
        self.assertEqual(0, data[0])
        self.assertEqual(0, data[1])
        self.assertEqual(1, data[2])
        self.assertEqual(1, data[3])
        self.assertEqual(2, data[4])
        self.assertEqual(2, data[5])
        self.assertEqual(3, data[6])
        self.assertEqual(4, data[7])
        self.assertEqual(6, data[8])
        self.assertEqual(7, data[9])
        self.assertEqual(8, data[10])
        self.assertEqual(9, data[11])
        self.assertEqual(11, data[12])
        self.assertEqual(12, data[13])
        self.assertEqual(23, data[14])

    def test_replaceRunsSpecific_no_runs_symbol_indata(self):
        """
        Purpose: Pass in data that has no runs of the specified symbol but has runs of other symbols. The symbol we are replacing is in the data
        Expectation: The data should be unchanged as there are no runs to replace
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [0, 0, 1, 1, 2, 2, 3, 4, 6, 7, 8, 9, 11, 12, 23])

        newLength = kompressor._replaceRunsSpecific(4, 257, 10, data, 15)

        self.assertEqual(15, newLength)
        self.assertEqual(0, data[0])
        self.assertEqual(0, data[1])
        self.assertEqual(1, data[2])
        self.assertEqual(1, data[3])
        self.assertEqual(2, data[4])
        self.assertEqual(2, data[5])
        self.assertEqual(3, data[6])
        self.assertEqual(4, data[7])
        self.assertEqual(6, data[8])
        self.assertEqual(7, data[9])
        self.assertEqual(8, data[10])
        self.assertEqual(9, data[11])
        self.assertEqual(11, data[12])
        self.assertEqual(12, data[13])
        self.assertEqual(23, data[14])

    def test_replaceRunsSpecific_run_at_beginning(self):
        """
        Purpose: Pass in data that has a run at the beginning of the sequence
        Expectation: The run should be replaced with the appropriate symbol
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [0, 0, 1, 1, 2, 2, 3, 4, 6, 7, 8, 9, 11, 12, 23])

        newLength = kompressor._replaceRunsSpecific(0, 258, 5, data, 15)

        self.assertEqual(14, newLength)
        self.assertEqual(258, data[0])
        self.assertEqual(1, data[1])
        self.assertEqual(1, data[2])
        self.assertEqual(2, data[3])
        self.assertEqual(2, data[4])
        self.assertEqual(3, data[5])
        self.assertEqual(4, data[6])
        self.assertEqual(6, data[7])
        self.assertEqual(7, data[8])
        self.assertEqual(8, data[9])
        self.assertEqual(9, data[10])
        self.assertEqual(11, data[11])
        self.assertEqual(12, data[12])
        self.assertEqual(23, data[13])

    def test_replaceRunsSpecific_run_at_end(self):
        """
        Purpose: Pass in data that has a run at the beginning of the sequence
        Expectation: The run should be replaced with the appropriate symbol
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [0, 0, 1, 1, 2, 2, 3, 4, 6, 7, 8, 9, 11, 11, 11])

        newLength = kompressor._replaceRunsSpecific(11, 259, 5, data, 15)

        self.assertEqual(13, newLength)
        self.assertEqual(0, data[0])
        self.assertEqual(0, data[1])
        self.assertEqual(1, data[2])
        self.assertEqual(1, data[3])
        self.assertEqual(2, data[4])
        self.assertEqual(2, data[5])
        self.assertEqual(3, data[6])
        self.assertEqual(4, data[7])
        self.assertEqual(6, data[8])
        self.assertEqual(7, data[9])
        self.assertEqual(8, data[10])
        self.assertEqual(9, data[11])
        self.assertEqual(260, data[12])

    def test_replaceRunsSpecific_run_several(self):
        """
        Purpose: Pass in data that has several runs of the symbol that needs to be replaced
        Expectation: The runs should be replaced with the appropriate symbol
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 9, 11, 11, 11, 5, 5, 4, 3, 3, 2, 2, 0, 0, 0, 0, 0])

        newLength = kompressor._replaceRunsSpecific(0, 259, 7, data, 27)

        self.assertEqual(16, newLength)
        self.assertEqual(260, data[0])
        self.assertEqual(1, data[1])
        self.assertEqual(2, data[2])
        self.assertEqual(263, data[3])
        self.assertEqual(9, data[4])
        self.assertEqual(11, data[5])
        self.assertEqual(11, data[6])
        self.assertEqual(11, data[7])
        self.assertEqual(5, data[8])
        self.assertEqual(5, data[9])
        self.assertEqual(4, data[10])
        self.assertEqual(3, data[11])
        self.assertEqual(3, data[12])
        self.assertEqual(2, data[13])
        self.assertEqual(2, data[14])
        self.assertEqual(262, data[15])

    def test_replaceRunsSpecific_run_past_max_by_1(self):
        """
        Purpose: Pass in data that has a run that exceeds the max by one character
        Expectation: Two symbols should be used to replace the run
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9])

        newLength = kompressor._replaceRunsSpecific(0, 259, 11, data, 18)

        self.assertEqual(6, newLength)
        self.assertEqual(260, data[0])
        self.assertEqual(1, data[1])
        self.assertEqual(2, data[2])
        self.assertEqual(268, data[3])
        self.assertEqual(0, data[4])
        self.assertEqual(9, data[5])

    def test_replaceRunsSpecific_run_past_max_by_maxminusone(self):
        """
        Purpose: Pass in data that has a run that exceeds the max by max minus one
        Expectation: Two symbols should be used to replace the run
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9])

        newLength = kompressor._replaceRunsSpecific(0, 259, 6, data, 17)

        self.assertEqual(6, newLength)
        self.assertEqual(260, data[0])
        self.assertEqual(1, data[1])
        self.assertEqual(2, data[2])
        self.assertEqual(263, data[3])
        self.assertEqual(262, data[4])
        self.assertEqual(9, data[5])

    def test_replaceRunsSpecific_run_past_max_by_max(self):
        """
        Purpose: Pass in data that has a run that exceeds the max by 2*max
        Expectation: Two symbols should be used to replace the run
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9])

        newLength = kompressor._replaceRunsSpecific(0, 259, 6, data, 18)

        self.assertEqual(6, newLength)
        self.assertEqual(260, data[0])
        self.assertEqual(1, data[1])
        self.assertEqual(2, data[2])
        self.assertEqual(263, data[3])
        self.assertEqual(263, data[4])
        self.assertEqual(9, data[5])

    def test_replaceRunsSpecific_run_past_max_by_2_max_plus_1(self):
        """
        Purpose: Pass in data that has a run that exceeds the max by 2*max
        Expectation: Two symbols should be used to replace the run
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9])

        newLength = kompressor._replaceRunsSpecific(0, 259, 6, data, 25)

        self.assertEqual(8, newLength)
        self.assertEqual(260, data[0])
        self.assertEqual(1, data[1])
        self.assertEqual(2, data[2])
        self.assertEqual(263, data[3])
        self.assertEqual(263, data[4])
        self.assertEqual(263, data[5])
        self.assertEqual(0, data[6])
        self.assertEqual(9, data[7])

    def test_replaceRunsSpecific_run_past_max_by_two(self):
        """
        Purpose: Pass in data that has a run that exceeds the max by 2
        Expectation: Two symbols should be used to replace the run
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 9])

        newLength = kompressor._replaceRunsSpecific(0, 259, 6, data, 14)

        self.assertEqual(6, newLength)
        self.assertEqual(260, data[0])
        self.assertEqual(1, data[1])
        self.assertEqual(2, data[2])
        self.assertEqual(263, data[3])
        self.assertEqual(259, data[4])
        self.assertEqual(9, data[5])

    def test_replaceRunsGeneric_no_data(self):
        """
        Purpose: Pass in array with no data
        Expectation: 0 should be returned
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [])

        newLength = kompressor._replaceRunsGeneric(259, 6, data, 0)

        self.assertEqual(0, newLength)

    def test_replaceRunsGeneric_two_symbols_no_runs(self):
        """
        Purpose: Pass in array with two symbols and no runs
        Expectation: The original data sequence should be returned
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 2])

        newLength = kompressor._replaceRunsGeneric(259, 6, data, 2)

        self.assertEqual(2, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(2, data[1])

    def test_replaceRunsGeneric_symbols_no_runs(self):
        """
        Purpose: Pass in array with a longer sequence of symbols that has no runs
        Expectation: The original data sequence should be returned
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17])

        newLength = kompressor._replaceRunsGeneric(259, 6, data, 17)

        self.assertEqual(17, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(2, data[1])
        self.assertEqual(3, data[2])
        self.assertEqual(4, data[3])
        self.assertEqual(5, data[4])
        self.assertEqual(6, data[5])
        self.assertEqual(7, data[6])
        self.assertEqual(8, data[7])
        self.assertEqual(9, data[8])
        self.assertEqual(10, data[9])
        self.assertEqual(11, data[10])
        self.assertEqual(12, data[11])
        self.assertEqual(13, data[12])
        self.assertEqual(14, data[13])
        self.assertEqual(15, data[14])
        self.assertEqual(16, data[15])
        self.assertEqual(17, data[16])

    def test_replaceRunsGeneric_run_of_2(self):
        """
        Purpose: Pass in array that has a run of two symbols
        Expectation: The run should be replaced by first symbol in run and the extended replacement symbol
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 2, 2, 3])

        newLength = kompressor._replaceRunsGeneric(259, 6, data, 4)

        self.assertEqual(4, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(2, data[1])
        self.assertEqual(259, data[2])
        self.assertEqual(3, data[3])

    def test_replaceRunsGeneric_run_of_3(self):
        """
        Purpose: Pass in array that has a run of three symbols
        Expectation: The run should be replaced by first symbol in run and the extended replacement symbol
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 44, 44, 44, 3])

        newLength = kompressor._replaceRunsGeneric(259, 6, data, 5)

        self.assertEqual(4, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(44, data[1])
        self.assertEqual(260, data[2])
        self.assertEqual(3, data[3])

    def test_replaceRunsGeneric_run_of_4(self):
        """
        Purpose: Pass in array that has a run of four symbols
        Expectation: The run should be replaced by first symbol in run and the extended replacement symbol
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 255, 255, 255, 255, 3])

        newLength = kompressor._replaceRunsGeneric(259, 6, data, 6)

        self.assertEqual(4, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(255, data[1])
        self.assertEqual(261, data[2])
        self.assertEqual(3, data[3])

    def test_replaceRunsGeneric_run_of_max(self):
        """
        Purpose: Pass in array that has a run of max allowed
        Expectation: The run should be replaced by first symbol in run and the replacement symbol
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 255, 255, 255, 255, 255, 255, 3])

        newLength = kompressor._replaceRunsGeneric(259, 6, data, 8)

        self.assertEqual(4, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(255, data[1])
        self.assertEqual(263, data[2])
        self.assertEqual(3, data[3])

    def test_replaceRunsGeneric_run_of_max_minus_1(self):
        """
        Purpose: Pass in array that has a run of max allowed minus one
        Expectation: The run should be replaced by first symbol in run and the extended symbol representing 5 additional duplicates
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 255, 255, 255, 255, 255, 3])

        newLength = kompressor._replaceRunsGeneric(259, 6, data, 7)

        self.assertEqual(4, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(255, data[1])
        self.assertEqual(262, data[2])
        self.assertEqual(3, data[3])

    def test_replaceRunsGeneric_run_of_max_plus_1(self):
        """
        Purpose: Pass in array that has a run of max allowed plus one
        Expectation: The run should be replaced by first symbol in run and the extended symbol representing max duplicates
                     and then extended symbol indicating 1 more duplicate
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 255, 255, 255, 255, 255, 255, 255, 3])

        newLength = kompressor._replaceRunsGeneric(259, 6, data, 9)

        self.assertEqual(5, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(255, data[1])
        self.assertEqual(263, data[2])
        self.assertEqual(259, data[3])
        self.assertEqual(3, data[4])

    def test_replaceRunsGeneric_run_of_max_plus_2_max_plus_1(self):
        """
        Purpose: Pass in array that has a run of 3 max allowed plus one
        Expectation: The runs should be replaced with correct extended symbols
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 3])

        newLength = kompressor._replaceRunsGeneric(259, 6, data, 21)

        self.assertEqual(7, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(255, data[1])
        self.assertEqual(263, data[2])
        self.assertEqual(263, data[3])
        self.assertEqual(263, data[4])
        self.assertEqual(261, data[5])
        self.assertEqual(3, data[6])

    def test_replaceRunsGeneric_run_of_2_runsize_0(self):
        """
        Purpose: Pass in array that has a run of two symbols but run size is 0
        Expectation: The data in the array should be unaffected
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 2, 2, 3])

        newLength = kompressor._replaceRunsGeneric(259, 0, data, 4)

        self.assertEqual(4, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(2, data[1])
        self.assertEqual(2, data[2])
        self.assertEqual(3, data[3])

    def test_replaceRunsGeneric_run_of_2_runsize_1(self):
        """
        Purpose: Pass in array that has a run of two symbols but run size is 1
        Expectation: The data in the array should be unaffected
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 2, 2, 3])

        newLength = kompressor._replaceRunsGeneric(259, 1, data, 4)

        self.assertEqual(4, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(2, data[1])
        self.assertEqual(2, data[2])
        self.assertEqual(3, data[3])

    def test_bytearrayLessThan_same(self):
        # Purpose: Compare the same permutation of bytearray
        # Expectation: 0 should be returned

        data = bytearray()

        #Create bytearray of len 11
        data.append(0)
        data.append(33)
        data.append(4)
        data.append(99)
        data.append(111)
        data.append(22)
        data.append(0)
        data.append(145)
        data.append(32)
        data.append(4)
        data.append(1)

        test_kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        self.assertEqual(0, test_kompressor._bytearrayLessThan(data, 0, 0, 11))
        self.assertEqual(0, test_kompressor._bytearrayLessThan(data, 1, 1, 11))
        self.assertEqual(0, test_kompressor._bytearrayLessThan(data, 5, 5, 11))
        self.assertEqual(0, test_kompressor._bytearrayLessThan(data, 10, 10, 11))

    def test_bytearrayLessThan_leftless(self):
        # Purpose: Compare the permutation when the left is less than the right
        # Expectation: -1 should be returned

        data = bytearray()

        #Create bytearray of len 11
        data.append(0)
        data.append(33)
        data.append(4)
        data.append(99)
        data.append(111)
        data.append(22)
        data.append(0)
        data.append(145)
        data.append(32)
        data.append(4)
        data.append(1)

        test_kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        self.assertEqual(-1, test_kompressor._bytearrayLessThan(data, 0, 1, 11))
        self.assertEqual(-1, test_kompressor._bytearrayLessThan(data, 1, 3, 11))
        self.assertEqual(-1, test_kompressor._bytearrayLessThan(data, 2, 3, 11))

    def test_bytearrayLessThan_rightless(self):
        # Purpose: Compare the permutation when the right is less than the left
        # Expectation: 1 should be returned

        data = bytearray()

        #Create bytearray of len 11
        data.append(0)
        data.append(33)
        data.append(4)
        data.append(99)
        data.append(111)
        data.append(22)
        data.append(0)
        data.append(145)
        data.append(32)
        data.append(4)
        data.append(1)

        test_kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        self.assertEqual(1, test_kompressor._bytearrayLessThan(data, 1, 0, 11))
        self.assertEqual(1, test_kompressor._bytearrayLessThan(data, 2, 6, 11))
        self.assertEqual(1, test_kompressor._bytearrayLessThan(data, 8, 9, 11))

    def test_performBWTransform_1(self):
        # Purpose: Run transform on small data set
        # Expectation: The resulting data should be transformed correctly

        data = array('i')

        #Create bytearray of len 11
        data.append(0)
        data.append(33)
        data.append(4)
        data.append(99)
        data.append(111)
        data.append(22)
        data.append(0)
        data.append(145)
        data.append(32)
        data.append(4)
        data.append(1)

        test_kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)


        transformedData = array('i', [0xFF]*12)

        test_kompressor._performBWTransform(data, 11, transformedData, 12)

        self.assertEqual(0, transformedData[0])
        self.assertEqual(1, transformedData[1])
        self.assertEqual(22, transformedData[2])
        self.assertEqual(4, transformedData[3])
        self.assertEqual(32, transformedData[4])
        self.assertEqual(33, transformedData[5])
        self.assertEqual(111, transformedData[6])
        self.assertEqual(145, transformedData[7])
        self.assertEqual(0, transformedData[8])
        self.assertEqual(4, transformedData[9])
        self.assertEqual(99, transformedData[10])
        self.assertEqual(0, transformedData[11])

    def test_performBWTransform_with_sectionsize_over256(self):
        # Purpose: Run transform on small data set
        # Expectation: The resulting data should be transformed correctly and the correct number of bytes should be prepended for transform

        data = array('i')

        #Create bytearray of len 11
        data.append(0)
        data.append(33)
        data.append(4)
        data.append(99)
        data.append(111)
        data.append(22)
        data.append(0)
        data.append(145)
        data.append(32)
        data.append(4)
        data.append(1)

        test_kompressor = Kompressor(1024, 0x00, 0, 0x00, 0, 10)

        transformedData = array('i', [0xFF]*13)

        outputLen = test_kompressor._performBWTransform(data, 11, transformedData, 13)

        self.assertEqual(13, outputLen)
        self.assertEqual(0, transformedData[0])
        self.assertEqual(0, transformedData[1])
        self.assertEqual(1, transformedData[2])
        self.assertEqual(22, transformedData[3])
        self.assertEqual(4, transformedData[4])
        self.assertEqual(32, transformedData[5])
        self.assertEqual(33, transformedData[6])
        self.assertEqual(111, transformedData[7])
        self.assertEqual(145, transformedData[8])
        self.assertEqual(0, transformedData[9])
        self.assertEqual(4, transformedData[10])
        self.assertEqual(99, transformedData[11])
        self.assertEqual(0, transformedData[12])

    def test_performBWTransform_2(self):
        # Purpose: Run transform on small data set
        # Expectation: The resulting data should be transformed correctly

        data = array('i')

        #Create bytearray of len 20
        data.append(0)
        data.append(33)
        data.append(4)
        data.append(99)
        data.append(111)
        data.append(22)
        data.append(0)
        data.append(145)
        data.append(32)
        data.append(4)
        data.append(21)
        data.append(4)
        data.append(199)
        data.append(111)
        data.append(4)
        data.append(0)
        data.append(1)
        data.append(3)
        data.append(7)
        data.append(8)

        test_kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)


        transformedData = array('i', [0xFF]*21)

        outputLen = test_kompressor._performBWTransform(data, 20, transformedData, 21)

        self.assertEqual(21, outputLen)
        self.assertEqual(1, transformedData[0])
        self.assertEqual(4, transformedData[1])
        self.assertEqual(8, transformedData[2])
        self.assertEqual(22, transformedData[3])
        self.assertEqual(0, transformedData[4])
        self.assertEqual(1, transformedData[5])
        self.assertEqual(111, transformedData[6])
        self.assertEqual(32, transformedData[7])
        self.assertEqual(33, transformedData[8])
        self.assertEqual(21, transformedData[9])
        self.assertEqual(3, transformedData[10])
        self.assertEqual(7, transformedData[11])
        self.assertEqual(4, transformedData[12])
        self.assertEqual(111, transformedData[13])
        self.assertEqual(145, transformedData[14])
        self.assertEqual(0, transformedData[15])
        self.assertEqual(4, transformedData[16])
        self.assertEqual(199, transformedData[17])
        self.assertEqual(99, transformedData[18])
        self.assertEqual(0, transformedData[19])
        self.assertEqual(4, transformedData[20])

    def test_performBWTransform_2_sectionsize_over_256(self):
        # Purpose: Run transform on small data set with the section size over 250 bytes
        # Expectation: The resulting data should be transformed correctly

        data = array('i')

        #Create bytearray of len 20
        data.append(0)
        data.append(33)
        data.append(4)
        data.append(99)
        data.append(111)
        data.append(22)
        data.append(0)
        data.append(145)
        data.append(32)
        data.append(4)
        data.append(21)
        data.append(4)
        data.append(199)
        data.append(111)
        data.append(4)
        data.append(0)
        data.append(1)
        data.append(3)
        data.append(7)
        data.append(8)

        test_kompressor = Kompressor(1024, 0x00, 0, 0x00, 0, 10)

        transformedData = array('i', [0xFF]*22)

        outputLen = test_kompressor._performBWTransform(data, 20, transformedData, 22)

        self.assertEqual(22, outputLen)
        self.assertEqual(1, transformedData[0])
        self.assertEqual(0, transformedData[1])
        self.assertEqual(4, transformedData[2])
        self.assertEqual(8, transformedData[3])
        self.assertEqual(22, transformedData[4])
        self.assertEqual(0, transformedData[5])
        self.assertEqual(1, transformedData[6])
        self.assertEqual(111, transformedData[7])
        self.assertEqual(32, transformedData[8])
        self.assertEqual(33, transformedData[9])
        self.assertEqual(21, transformedData[10])
        self.assertEqual(3, transformedData[11])
        self.assertEqual(7, transformedData[12])
        self.assertEqual(4, transformedData[13])
        self.assertEqual(111, transformedData[14])
        self.assertEqual(145, transformedData[15])
        self.assertEqual(0, transformedData[16])
        self.assertEqual(4, transformedData[17])
        self.assertEqual(199, transformedData[18])
        self.assertEqual(99, transformedData[19])
        self.assertEqual(0, transformedData[20])
        self.assertEqual(4, transformedData[21])

    def test_performBWTransform_3(self):
        # Purpose: Run transform on larger data set
        # Expectation: The resulting data should be transformed correctly

        data = array('i',[0x50,0xb9,0x71,0xd5,0x98,0x9f,0xaa,0x1e,0x50,0xb9,0x71,0xd5,0x1c,0x00,0xa6,0x1a,
                          0x55,0x3d,0x14,0x0f,0xf5,0x01,0x40,0x08,0x07,0x04,0x89,0x00,0x00,0x00,0xa0,0x11,
                          0x03,0x20,0x14,0x0f,0xde,0xb9,0x6b,0x1e,0xad,0xc3,0x07,0xbc,0x01,0xf0,0x44,0x37,
                          0x17,0xa7,0xb0,0xec,0x18,0x00,0xa6,0x1a,0x32,0x3d,0x14,0x0f,0xf5,0x01,0x75,0x05,
                          0x76,0x09,0x75,0x00,0x02,0x01,0x00,0x03,0x2b,0x3d,0x14,0x0f,0xf1,0xee,0x0b,0x00,
                          0x50,0x10,0x00,0xb0,0x15,0xa7,0xb0,0xec,0x18,0x00,0xa6,0x01,0x35,0x3d,0x14,0x0f,
                          0xf5,0x01,0x97,0x05,0x03,0x09,0x65,0x00,0x02,0x01,0x02,0xa8,0x28,0x3d,0x14,0x0f,
                          0xf2,0xee,0x0b,0x00,0x50,0x10,0x00,0xb0,0x1d,0xa7,0xb0,0xec,0x18,0x00,0xa6,0x07,
                          0x20,0x3d,0x14,0x0f,0xf5,0x01,0xd9,0x05,0x02,0x08,0x88,0x00,0x02,0x01,0x02,0xb1,
                          0x1c,0x3d,0x14,0x0f,0xf1,0xee,0x0b,0x00,0x50,0x30,0x00,0xb5])



        test_kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        transformedData = array('i', [0]*157)

        test_kompressor._performBWTransform(data, 156, transformedData, 157)

    def test_kompress_small_data_set(self):
        # Purpose: Compress a small data set with special symbols 1 and 2
        # Expectation: The encoded data should match what is expected

        data = array('i',[0x01, 0x01, 0x02, 0x03, 0x03, 0x05, 0x03, 0x04, 0x04])
        outData = bytearray(256)

        test_kompressor = Kompressor(256, 0x01, 2, 0x03, 2, 10)

        simpleEncoder = SimpleEncoder(test_kompressor.mVocabularySize)
        test_kompressor.mEncoder = simpleEncoder

        compressedData = test_kompressor.kompress(data, 9, outData, 256)

        self.assertEqual(9, compressedData)
        self.assertEqual(0x07, simpleEncoder.mEncodedData[0])
        self.assertEqual(257, simpleEncoder.mEncodedData[1])
        self.assertEqual(0x02, simpleEncoder.mEncodedData[2])
        self.assertEqual(0x05, simpleEncoder.mEncodedData[3])
        self.assertEqual(259, simpleEncoder.mEncodedData[4])
        self.assertEqual(0x04, simpleEncoder.mEncodedData[5])
        self.assertEqual(0x03, simpleEncoder.mEncodedData[6])
        self.assertEqual(0x04, simpleEncoder.mEncodedData[7])
        self.assertEqual(256, simpleEncoder.mEncodedData[8])

    def test_kompress_small_data_set_onlyspecial_symbol1(self):
        # Purpose: Compress a small data set with special symbols 1 only
        # Expectation: The encoded data should match what is expected

        data = array('i',[0x01, 0x01, 0x02, 0x03, 0x03])
        outData = bytearray(256)

        test_kompressor = Kompressor(256, 0x01, 2, 0x03, 0, 10)

        simpleEncoder = SimpleEncoder(test_kompressor.mVocabularySize)
        test_kompressor.mEncoder = simpleEncoder

        compressedData = test_kompressor.kompress(data, 5, outData, 256)

        self.assertEqual(6, compressedData)
        self.assertEqual(0x03, simpleEncoder.mEncodedData[0])
        self.assertEqual(257, simpleEncoder.mEncodedData[1])
        self.assertEqual(0x02, simpleEncoder.mEncodedData[2])
        self.assertEqual(0x03, simpleEncoder.mEncodedData[3])
        self.assertEqual(259, simpleEncoder.mEncodedData[4])
        self.assertEqual(256, simpleEncoder.mEncodedData[5])

    def test_kompress_small_data_set_onlyspecial_symbol2(self):
        # Purpose: Compress a small data set with special symbols 2 only
        # Expectation: The encoded data should match what is expected

        data = array('i',[0x01, 0x01, 0x02, 0x03, 0x03])
        outData = bytearray(256)

        test_kompressor = Kompressor(256, 0x01, 0, 0x03, 2, 10)

        simpleEncoder = SimpleEncoder(test_kompressor.mVocabularySize)
        test_kompressor.mEncoder = simpleEncoder

        compressedData = test_kompressor.kompress(data, 5, outData, 256)

        self.assertEqual(7, compressedData)
        self.assertEqual(0x00, simpleEncoder.mEncodedData[0])
        self.assertEqual(0x03, simpleEncoder.mEncodedData[1])
        self.assertEqual(0x01, simpleEncoder.mEncodedData[2])
        self.assertEqual(259, simpleEncoder.mEncodedData[3])
        self.assertEqual(0x03, simpleEncoder.mEncodedData[4])
        self.assertEqual(0x02, simpleEncoder.mEncodedData[5])
        self.assertEqual(256, simpleEncoder.mEncodedData[6])

    def test_kompress_medium_data_set(self):
        # Purpose: Compress a medium data set with special symbols 1 and 2
        # Expectation:

        data = array('i',[0x50,0xb9,0x71,0xd5,0x98,0x9f,0xaa,0x1e,0x50,0xb9,0x71,0xd5,0x1c,0x00,0xa6,0x1a,
                          0x55,0x3d,0x14,0x0f,0xf5,0x01,0x40,0x08,0x07,0x04,0x89,0x00,0x00,0x00,0xa0,0x11,
                          0x03,0x20,0x14,0x0f,0xde,0xb9,0x6b,0x1e,0xad,0xc3,0x07,0xbc,0x01,0xf0,0x44,0x37,
                          0x17,0xa7,0xb0,0xec,0x18,0x00,0xa6,0x1a,0x32,0x3d,0x14,0x0f,0xf5,0x01,0x75,0x05,
                          0x76,0x09,0x75,0x00,0x02,0x01,0x00,0x03,0x2b,0x3d,0x14,0x0f,0xf1,0xee,0x0b,0x00,
                          0x50,0x10,0x00,0xb0,0x15,0xa7,0xb0,0xec,0x18,0x00,0xa6,0x01,0x35,0x3d,0x14,0x0f,
                          0xf5,0x01,0x97,0x05,0x03,0x09,0x65,0x00,0x02,0x01,0x02,0xa8,0x28,0x3d,0x14,0x0f,
                          0xf2,0xee,0x0b,0x00,0x50,0x10,0x00,0xb0,0x1d,0xa7,0xb0,0xec,0x18,0x00,0xa6,0x07,
                          0x20,0x3d,0x14,0x0f,0xf5,0x01,0xd9,0x05,0x02,0x08,0x88,0x00,0x02,0x01,0x02,0xb1,
                          0x1c,0x3d,0x14,0x0f,0xf1,0xee,0x0b,0x00,0x50,0x30,0x00,0xb5])

        outData = bytearray(256)

        test_kompressor = Kompressor(256, 0x00, 5, 0x00, 5, 5)

        simpleEncoder = SimpleEncoder(test_kompressor.mVocabularySize)
        test_kompressor.mEncoder = simpleEncoder

        compressedData = test_kompressor.kompress(data, 156, outData, 256)

        self.assertEqual(125, compressedData)

    def test_kompress_medium_data_set_2(self):
        # Purpose: Compress a medium data set with special symbols 1 and 2
        # Expectation:

        data = array('i', [0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                           0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                           0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                           0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                           0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                           0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                           0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                           0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                           0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                           0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                           0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                           0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                           0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                           0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                           0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                           0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                           0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                           0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                           0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                           0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03])

        outData = bytearray(256)

        test_kompressor = Kompressor(256, 0x00, 5, 0x00, 5, 5)

        simpleEncoder = SimpleEncoder(test_kompressor.mVocabularySize)
        test_kompressor.mEncoder = simpleEncoder

        compressedData = test_kompressor.kompress(data, 160, outData, 256)

        self.assertEqual(119, compressedData)

    def test_kompress_medium_data_set_AREncoer(self):
        # Purpose: Compress a medium data set with special symbols 1 and 2 and using AREncoder
        # Expectation:

        data = array('i', [0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                           0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                           0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                           0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                           0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                           0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                           0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                           0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                           0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                           0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03,
                           0xfb,0xbb,0x71,0xd5,0x1c,0x00,0xa6,0x0a,
                           0x8c,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                           0x07,0x04,0xbc,0x00,0x00,0x00,0x92,0x11,
                           0x8b,0x18,0x49,0x0e,0xfd,0x41,0x7b,0x1f,
                           0xb4,0xb9,0x95,0xbb,0x00,0xf8,0xbc,0x02,
                           0x86,0xaa,0xb0,0xec,0x1c,0x00,0xa6,0x0b,
                           0x81,0x18,0x49,0x0e,0xf5,0x01,0x00,0x00,
                           0x03,0x06,0x8b,0x00,0x00,0x00,0x8f,0x11,
                           0x7a,0x18,0x49,0x0e,0x59,0x40,0x7b,0x1f,
                           0x60,0xbe,0x95,0xbb,0x00,0x74,0x8b,0x03])

        outData = bytearray(256)

        test_kompressor = Kompressor(256, 0x00, 5, 0x00, 5, 5)

        compressedData = test_kompressor.kompress(data, 160, outData, 256)

        self.assertEqual(100, compressedData)

if __name__ == '__main__':
    unittest.main()

