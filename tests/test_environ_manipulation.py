import random
import string
import unittest
import sys
import os

sys.path.append("/".join(os.getcwd().split("/")[:-1]) + "/backend/")

import environ_manipulation

class ApplicationTest(unittest.TestCase):
    def test_handler_valid(self):
        for i in range(100):
            exp = "".join(random.choice(list(string.ascii_letters)) for i in range(random.randint(10, 100)))

            environ = {"REQUEST_URI": "/cgi-bin/" + exp + "/target"}
            # Model of the environ dictionary, with the only used parameter in it.

            out = environ_manipulation.application.get_target(environ)

            assert (exp == out)

    def test_handler_invalid(self):
        for i in range(100):
            exp = "".join(random.choice(list(string.ascii_letters)) for i in range(random.randint(10, 100)))

            environ = {"REQUEST_URI": "/cgi-bin/" + exp}
            # Model of the environ dictionary, with the only used parameter in it.

            out = environ_manipulation.application.get_target(environ)

            assert (exp == out)

        environ = {"REQUEST_URI": "/cgi-bin/"}
        # Model of the environ dictionary, with the only used parameter in it.

        out = environ_manipulation.application.get_target(environ)

        assert (out == None)

    def test_function_valid(self):
        for i in range(100):
            exp = "".join(random.choice(list(string.ascii_letters)) for i in range(random.randint(10, 100)))

            environ = {"REQUEST_URI": "/cgi-bin/handler/" + exp}
            # Model of the environ dictionary, with the only used parameter in it.

            out = environ_manipulation.application.get_sub_target(environ)

            assert (exp == out)

    def test_function_invalid(self):
        environ = {"REQUEST_URI": "/cgi-bin/handler/"}
        # Model of the environ dictionary, with the only used parameter in it.
        out = environ_manipulation.application.get_sub_target(environ)

        assert (out == None)

        environ = {"REQUEST_URI": "/cgi-bin/"}
        # Model of the environ dictionary, with the only  used parameter in it.
        out = environ_manipulation.application.get_sub_target(environ)

        assert (out == None)


if __name__ == '__main__':
    unittest.main()
