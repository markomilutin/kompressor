__author__ = 'Marko Milutinovic'

import unittest
from array import array

from Kompressor import Kompressor

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
        self.assertEqual(0xFF, kompressor.mSpecialSymbol2)
        self.assertEqual(4, kompressor.mSpecialSymbol2MaxRun)
        self.assertEqual(10, kompressor.mGenericMaxRun)
        self.assertEqual(257+3+4+10, kompressor.mVocabularySize)
        self.assertEqual(1, kompressor.mBWTransforStoreBytes)
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
        Expectation: The run should be replaced by first symbol in run and the max replacement symbol
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 255, 255, 255, 255, 255, 255, 3])

        newLength = kompressor._replaceRunsGeneric(259, 6, data, 8)

        self.assertEqual(4, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(255, data[1])
        self.assertEqual(263, data[2])
        self.assertEqual(3, data[3])

    def test_replaceRunsGeneric_run_of_max_plus_1(self):
        """
        Purpose: Pass in array that has a run of max allowed plus one
        Expectation: The run should be replaced by first symbol in run and the max replacement symbol and then the original run symbol again
        """

        kompressor = Kompressor(256, 0x00, 0, 0x00, 0, 10)

        data = array('i', [1, 255, 255, 255, 255, 255, 255, 255, 3])

        newLength = kompressor._replaceRunsGeneric(259, 6, data, 9)

        self.assertEqual(5, newLength)
        self.assertEqual(1, data[0])
        self.assertEqual(255, data[1])
        self.assertEqual(263, data[2])
        self.assertEqual(255, data[3])
        self.assertEqual(3, data[4])

if __name__ == '__main__':
    unittest.main()

