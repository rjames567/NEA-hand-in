# python3 -m unittest -v test_data_structures.py
import string
import unittest
import random
import sys
import os
from queue import PriorityQueue as TruePriorityQueue


sys.path.append("/".join(os.getcwd().split("/")[:-1]) + "/backend/")

import data_structures as structures

class QueueTest(unittest.TestCase):
    def test_order(self):
        queue = structures.Queue()
        items = [random.randrange(0, 100) for i in range(100)]
        for i in items:
            queue.push(i)

        out = [queue.pop() for i in range(100)]

        assert(items == out)

    def test_overflow(self):
        queue = structures.Queue(max_length=100)
        for i in range(100):
            queue.push(random.randrange(0, 100))


        self.assertRaises(
            structures.QueueOverflowError,
            queue.push,
            random.random()
        )

    def test_underflow(self):
        queue = structures.Queue()

        self.assertRaises(
            structures.QueueUnderflowError,
            queue.pop
        )

class PriorityQueueTest(unittest.TestCase):
    def test_order_val(self):
        queue = structures.PriorityQueue()

        items = [random.randrange(0, 15) for i in range(100)]
        for i in items:
            queue.push(i)

        items.sort(reverse=True)  # priority is done as largest numbers are
        # most important

        out = [queue.pop() for i in range(100)]

        assert(items == out)

    def test_order_func(self):
        # assume built-in is true
        queue = structures.PriorityQueue(lambda x: x[1])
        true_queue = TruePriorityQueue()

        items = [[i, random.randrange(0, 15)] for i in range(100)]
        for i in items:
            true_queue.put((-i[0], i[1]))  # Sorts the opposite way to custom
            # implementation
            queue.push((i[1], i[0]))

        items = [true_queue.get()[1] for i in range(100)]

        out = [queue.pop()[0] for i in range(100)]

        assert(items == out)

    def test_underflow(self):
        queue = structures.PriorityQueue()

        self.assertRaises(
            structures.QueueUnderflowError,
            queue.pop
        )

    def test_overflow(self):
        queue = structures.PriorityQueue(max_length=100)
        for i in range(100):
            queue.push(random.randrange(0, 100))

        self.assertRaises(
            structures.QueueOverflowError,
            queue.push,
            random.random()
        )

class TestBinaryTree(unittest.TestCase):
    def test_inorder(self):
        tree = structures.BinaryTree()

        expected = []

        for i in range(100):
            val = random.randrange(0, 10)
            tree.insert(val)
            expected.append(val)

        expected.sort()

        out = tree.in_order_traversal()

        assert(out == expected)

    def test_inorder_access(self):
        tree = structures.BinaryTree(access_function=lambda x: x[0])

        expected = []

        for i in range(100):
            c = random.choice(list(string.ascii_lowercase))
            val = random.randrange(0, 10)
            tree.insert((val, c))
            expected.append((val, c))

        expected.sort(key=lambda x: x[0])

        out = tree.in_order_traversal()

        assert (out == expected)


class StackTest(unittest.TestCase):
    def test_order(self):
        stack = structures.Stack()
        items = [random.randrange(0, 100) for i in range(100)]

        for i in items:
            stack.push(i)

        out = [stack.pop() for i in range(100)]

        items.reverse()  # Stack is FILO, so FIFO items needs to be reversed

        assert (items == out)

    def test_overflow(self):
        stack = structures.Stack(max_length=100)
        for i in range(100):
            stack.push(random.randrange(0, 100))

        self.assertRaises(
            structures.StackOverflowError,
            stack.push,
            random.random()
        )

    def test_underflow(self):
        stack = structures.Stack()

        self.assertRaises(
            structures.StackUnderflowError,
            stack.pop
        )

if __name__ == '__main__':
    unittest.main()
