__author__ = 'Marko Milutinovic'

import unittest
from array import array

from Dekompressor import Dekompressor
from SimpleDecoder import SimpleDecoder

class KompressorTests(unittest.TestCase):
    def test_constructor(self):
        """
        Purpose: Instantiate an object
        Expectation: The member variables should be initialized correctly
        """

        dekompressor = Dekompressor(256, 0x00, 3, 0xFF, 4, 10)

        self.assertEqual(256, dekompressor.mSectionSize)
        self.assertEqual(0, dekompressor.mSpecialSymbol1)
        self.assertEqual(3, dekompressor.mSpecialSymbol1MaxRun)
        self.assertEqual(257, dekompressor.mSpecialSymbol1RunLengthStart)
        self.assertEqual(0xFF, dekompressor.mSpecialSymbol2)
        self.assertEqual(4, dekompressor.mSpecialSymbol2MaxRun)
        self.assertEqual(260, dekompressor.mSpecialSymbol2RunLengthStart)
        self.assertEqual(10, dekompressor.mGenericMaxRun)
        self.assertEqual(264, dekompressor.mGenericRunLengthStart)
        self.assertEqual(257+3+4+10, dekompressor.mVocabularySize)
        self.assertEqual(1, dekompressor.mBWTransformStoreBytes)
        self.assertNotEqual(None, dekompressor.mSectionTransformData)
        self.assertEqual(257, len(dekompressor.mSectionTransformData))
        self.assertEqual(257, dekompressor.mSectionTransformDataMaxSize)
        self.assertNotEqual(None, dekompressor.mDecoder)
        self.assertEqual(False, dekompressor.mContinuousModeEnabled)
        self.assertEqual(0, dekompressor.mContinuousModeTotalData)
        self.assertEqual(0, dekompressor.mContinuousModeDataCompressed)


if __name__ == '__main__':
    unittest.main()
