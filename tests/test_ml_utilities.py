import random
import string
import unittest
import sys
import os

sys.path.append("/".join(os.getcwd().split("/")[:-1]) + "/backend/")

import ml_utilities

class ApplicationTest(unittest.TestCase):
    def test_jaccard_valid(self):
        set1 = set([3, 4, 10, 5, 230, 67, 90])
        set2 = set([7, 8, 10, 3, 4, 5, 100230])

        exp = 4/10

        out = ml_utilities.jaccard_similarity(set1, set2)

        assert (exp == out)

    # mean_squared_error is not used


if __name__ == '__main__':
    unittest.main()
