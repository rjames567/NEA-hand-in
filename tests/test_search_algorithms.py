import random
import unittest
import sys
import os

sys.path.append("/".join(os.getcwd().split("/")[:-1]) + "/backend/")

import searching_algorithms

class BinaryTest(unittest.TestCase):
    def test_binary_search(self):
        available = list(range(10000))
        nums = []

        for i in range(10):
            num = random.randint(0, len(available) - 1)
            nums.append(available[num])
            available.pop(num)

        nums.sort()

        target = random.choice(nums)

        print(nums)

        out = searching_algorithms.binary_search(nums, target)
        exp = nums.index(target)

        print(out, exp)

        assert (out == exp)


if __name__ == '__main__':
    unittest.main()
