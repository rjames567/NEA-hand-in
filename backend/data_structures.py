# ------------------------------------------------------------------------------
# Standard Python library imports
# ------------------------------------------------------------------------------
import math
import itertools

# ------------------------------------------------------------------------------
# Project imports
# ------------------------------------------------------------------------------
import searching_algorithms

# ------------------------------------------------------------------------------
# Custom exceptions
# ------------------------------------------------------------------------------
class QueueOverflowError(Exception):
    def __init__(self):
        super().__init__("Tried to push too many items into the queue")


class QueueUnderflowError(Exception):
    def __init__(self):
        super().__init__("Tried to get a value from an empty queue")


class StackOverflowError(Exception):
    def __init__(self):
        super().__init__("Tried to push too many items into the stack")


class StackUnderflowError(Exception):
    def __init__(self):
        super().__init__("Tried to get a value from an empty stack")


# ------------------------------------------------------------------------------
# Queue
# ------------------------------------------------------------------------------
class Queue:
    def __init__(self, max_length=None):
        self._items = []
        self._max_length = max_length

    def push(self, item):
        if self._max_length is not None and self.size + 1 > self._max_length:
            # Checks if it is not None, and if so does not check second clause
            raise QueueOverflowError
        self._items.append(item)  # Appends to end

    def pop(self):
        if not self.size:
            raise QueueUnderflowError
        return self._items.pop(0)  # List is reverse order - FILO

    def peek(self):
        if not self.size:
            raise QueueUnderflowError
        return self._items[0]

    @property
    def size(self):
        return len(self._items)


class PriorityQueue(Queue):
    def __init__(self, priority_func=None, max_length=None):
        super().__init__(max_length=max_length)
        if priority_func is None:
            self._priority_func = lambda x: x
        else:
            self._priority_func = priority_func

    def push(self, item, priority=None):
        if self._max_length is not None and self.size + 1 > self._max_length:
            # Checks if it is not None, and if so does not check second clause
            raise QueueOverflowError

        if priority is None:
            priority = self._priority_func(item)
            
        self._items.append((item, priority))

        self._items.sort(key=lambda x: x[1], reverse=True)

    def pop(self):
        return super().pop()[0]  # The result from the super would be a list, where the first item is the inserted value
        # and the second is the priority

    def peek(self):
        return super().peek()[0]

# ------------------------------------------------------------------------------
# Stack
# ------------------------------------------------------------------------------
class Stack:
    def __init__(self, max_length=None):
        self._items = []
        self._max_length = max_length

    def push(self, item):
        if self._max_length is not None and self.size + 1 > self._max_length:
            raise StackOverflowError
        self._items.append(item)

    def pop(self):
        if not self.size:
            raise StackUnderflowError
        return self._items.pop(-1)

    def peek(self):
        return self._items[-1]

    @property
    def size(self):
        return len(self._items)

# ------------------------------------------------------------------------------
# Binary Tree
# ------------------------------------------------------------------------------
# https://www.tutorialspoint.com/python_data_structure/python_binary_tree.htm
class BinaryTree:
    def __init__(self, value=None, access_function=None):
        self.left = self.right = None
        self.value = value
        if access_function is None:
            self.access_function = lambda x: x
        else:
            self.access_function = access_function

    def insert(self, value):
        if self.value is None:
            self.value = value
        else:
            if self.access_function(value) < self.access_function(self.value):
                if self.left:
                    self.left.insert(value)
                else:
                    self.left = BinaryTree(value, self.access_function)
            else:
                if self.right:
                    self.right.insert(value)
                else:
                    self.right = BinaryTree(value, self.access_function)

    def in_order_traversal(self, root=""):
        if root == "":  # Cannot be None, and an empty string cannot be used.
            root = self
        res = []
        if root is not None:
            res = self.in_order_traversal(root.left)
            res.append(root.value)
            res = res + self.in_order_traversal(root.right)
        return res
