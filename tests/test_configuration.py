# python3 -m unittest -v test_configuration.py

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backend.configuration as configuration


class IntegerTest(unittest.TestCase):
    def test_positive_integer(self):
        config = configuration.Configuration("tests/test_configurations/integer_positive.conf")
        assert(config.get("value1") == 2)
        assert(type(config.get("value1")) == int)

        assert(config.get("value2") == 5678923423)
        assert (type(config.get("value2")) == int)

        assert(config.get("value3") == 10)
        assert (type(config.get("value3")) == int)

        assert(config.get("value4") == 567)
        assert (type(config.get("value4")) == int)

    def test_negative_integer(self):
        config = configuration.Configuration("tests/test_configurations/integer_negative.conf")
        assert (config.get("value1") == -2)
        assert (type(config.get("value1")) == int)

        assert (config.get("value2") == -5678923423)
        assert (type(config.get("value2")) == int)

        assert (config.get("value3") == -10)
        assert (type(config.get("value3")) == int)

        assert (config.get("value4") == -567)
        assert (type(config.get("value4")) == int)

    def test_positve_expression(self):
        config = configuration.Configuration("tests/test_configurations/integer_positive_expression.conf")
        assert (config.get("value1") == (1*10**2))
        assert (type(config.get("value1")) == int)

        assert (config.get("value2") == (1*10**5))
        assert (type(config.get("value2")) == int)

        assert (config.get("value3") == (3.23*10**4))
        assert (type(config.get("value3")) == int)

        assert (config.get("value4") == (1*10**46))
        assert (type(config.get("value4")) == int)

    def test_negative_expression(self):
        config = configuration.Configuration("tests/test_configurations/integer_negative_expression.conf")
        assert (config.get("value1") == (-1*10**2))
        assert (type(config.get("value1")) == int)

        assert (config.get("value2") == (-1*10**5))
        assert (type(config.get("value2")) == int)

        assert (config.get("value3") == (-3.23*10**4))
        assert (type(config.get("value3")) == int)

        assert (config.get("value4") == (-1*10**46))
        assert (type(config.get("value4")) == int)

    def test_invalid_integer(self):
        self.assertRaises(
            configuration.ConfigInvalidDataForType,
            configuration.Configuration,
            "tests/test_configurations/integer_invalid.conf"
        )  # Error is thrown when config passed


class StringTest(unittest.TestCase):
    def test_values(self):
        config = configuration.Configuration("tests/test_configurations/string.conf")
        assert (config.get("value1") == "string" and type(config.get("value1")) == str)
        assert (config.get("value2") == "string 2 with spaces & special characters!" and type(config.get("value2")) == str)
        assert (config.get("value3") == "450" and type(config.get("value3")) == str)
        assert (config.get("value4") == "-450" and type(config.get("value4")) == str)
        assert (config.get("value5") == "true" and type(config.get("value5")) == str)
        assert (config.get("value6") == "false" and type(config.get("value6")) == str)
        assert (config.get("value7") == "6.901" and type(config.get("value7")) == str)
        assert (config.get("value8") == "-6.901" and type(config.get("value8")) == str)


class FloatTest(unittest.TestCase):
    def test_floating_point(self):
        config = configuration.Configuration("tests/test_configurations/floating_point_valid.conf")
        assert (config.get("value1") == 1.02 and type(config.get("value1")) == float)
        assert (config.get("value2") == 6002.30523 and type(config.get("value2")) == float)
        assert (config.get("value3") == 10 and type(config.get("value3")) == float)
        assert (config.get("value4") == -1.02 and type(config.get("value3")) == float)
        assert (config.get("value5") == -6002.30523 and type(config.get("value4")) == float)
        assert (config.get("value6") == -10 and type(config.get("value6")) == float)

    def test_integer(self):
        config = configuration.Configuration("tests/test_configurations/floating_point_integer.conf")
        assert (config.get("value1") == 10032 and type(config.get("value1")) == float)
        assert (config.get("value2") == 123 and type(config.get("value2")) == float)
        assert (config.get("value3") == -10032 and type(config.get("value3")) == float)
        assert (config.get("value4") == -123 and type(config.get("value4")) == float)

    def test_positve_expression(self):
        config = configuration.Configuration("tests/test_configurations/float_positive_expression.conf")
        assert (config.get("value1") == (1.0001 * 10 ** 2))
        assert (type(config.get("value1")) == float)

        assert (config.get("value2") == (1 * 10 ** -5))
        assert (type(config.get("value2")) == float)

        assert (config.get("value3") == (3.23 * 10 ** -4))
        assert (type(config.get("value3")) == float)

        assert (config.get("value4") == (1 * 10 ** -46))
        assert (type(config.get("value4")) == float)

    def test_negative_expression(self):
        config = configuration.Configuration("tests/test_configurations/float_negative_expression.conf")
        assert (config.get("value1") == (-1.0001 * 10 ** 2))
        assert (type(config.get("value1")) == float)

        assert (config.get("value2") == (-1 * 10 ** -5))
        assert (type(config.get("value2")) == float)

        assert (config.get("value3") == (-3.23 * 10 ** -4))
        assert (type(config.get("value3")) == float)

        assert (config.get("value4") == (-1 * 10 ** -46))
        assert (type(config.get("value4")) == float)

    def test_invalid(self):
        self.assertRaises(
            configuration.ConfigInvalidDataForType,
            configuration.Configuration,
            "tests/test_configurations/floating_point_invalid.conf"
        )  # Error is thrown when config passed

class BinaryTest(unittest.TestCase):
    def test_string(self):
        config = configuration.Configuration("tests/test_configurations/binary_string.conf")
        assert (config.get("value1") == "string".encode("utf-8") and type(config.get("value1")) == bytes)
        assert (config.get("value2") == "string 2 & special characters!".encode("utf-8") and type(config.get("value2")) == bytes)
        assert (config.get("value3") == "true".encode("utf-8") and type(config.get("value3")) == bytes)
        assert (config.get("value4") == "false".encode("utf-8") and type(config.get("value4")) == bytes)

    def test_integers(self):
        config = configuration.Configuration("tests/test_configurations/binary_int.conf")
        assert (config.get("value1") == "1232".encode("utf-8") and type(config.get("value1")) == bytes)
        assert (config.get("value2") == "-1232".encode("utf-8") and type(config.get("value2")) == bytes)

    def test_floating_point(self):
        config = configuration.Configuration("tests/test_configurations/binary_float.conf")
        assert (config.get("value1") == "123.563".encode("utf-8") and type(config.get("value1")) == bytes)
        assert (config.get("value2") == "-123.563".encode("utf-8") and type(config.get("value2")) == bytes)


class BooleanTest(unittest.TestCase):
    def test_boolean(self):
        config = configuration.Configuration("tests/test_configurations/bool_valid.conf")
        assert (config.get("value1") == True and type(config.get("value1")) == bool)
        assert (config.get("value2") == False and type(config.get("value2")) == bool)

    def test_integer(self):
        self.assertRaises(
            configuration.ConfigInvalidDataForType,
            configuration.Configuration,
            "tests/test_configurations/bool_int.conf"
        )

    def test_string(self):
        self.assertRaises(
            configuration.ConfigInvalidDataForType,
            configuration.Configuration,
            "tests/test_configurations/bool_string.conf"
        )

    def test_float(self):
        self.assertRaises(
            configuration.ConfigInvalidDataForType,
            configuration.Configuration,
            "tests/test_configurations/bool_float.conf"
        )

class HeirachyTest(unittest.TestCase):
    def test_heirachy_misc(self):
        config = configuration.Configuration("tests/test_configurations/heirachy_misc.conf")
        assert (config.get("header1 value1") == False and type(config.get("header1 value1")) == bool)
        assert (config.get("header1 value2") == True and type(config.get("header1 value2")) == bool)
        assert (config.get("header2 value1") == "string" and type(config.get("header2 value1")) == str)
        assert (config.get("header2 value2") == 1.2 and type(config.get("header2 value2")) == float)
        assert (config.get("misc1") == "hello world" and type(config.get("misc1")) == str)


    def test_heirachy_misc_heirachy(self):
        config = configuration.Configuration("tests/test_configurations/heirachy_misc_heirachy.conf")
        assert (config.get("header1 value1") == False and type(config.get("header1 value1")) == bool)
        assert (config.get("header1 value2") == True and type(config.get("header1 value2")) == bool)
        assert (config.get("header2 value1") == "string" and type(config.get("header2 value1")) == str)
        assert (config.get("header2 value2") == 1.2 and type(config.get("header2 value2")) == float)
        assert (config.get("misc1") == "hello world" and type(config.get("misc1")) == str)


class DefaultConfigurationTest(unittest.TestCase):
    def test_unknown_default(self):
        self.assertRaises(
            FileNotFoundError,
            configuration.Configuration,
            "tests/test_configurations/invalid_datatype.conf",
            "tests/test_configurations/non_existent_file.json"
        )

    def test_default_file(self):
        config = configuration.Configuration(
            "tests/test_configurations/empty.conf",
            "tests/test_configurations/default_configuration.json"
        )
        assert (config.get("header1 value1") == 4 and type(config.get("header1 value1")) == int)
        assert (config.get("header1 value2") == 3.5 and type(config.get("header1 value2")) == float)
        assert (config.get("header2 value1") == "hello" and type(config.get("header2 value1")) == str)
        assert (config.get("header2 value2") == True and type(config.get("header2 value2")) == bool)
        assert (config.get("misc1") == False and type(config.get("misc1")) == bool)

    def test_default_file_addition(self):
        config = configuration.Configuration(
            "tests/test_configurations/default_add.conf",
            "tests/test_configurations/default_configuration.json"
        )
        assert (config.get("header1 value1") == 4 and type(config.get("header1 value1")) == int)
        assert (config.get("header1 value2") == 3.5 and type(config.get("header1 value2")) == float)
        assert (config.get("header2 value1") == "hello" and type(config.get("header2 value1")) == str)
        assert (config.get("header2 value2") == True and type(config.get("header2 value2")) == bool)
        assert (config.get("misc1") == False and type(config.get("misc1")) == bool)


        assert (config.get("header1 value3") == "string" and type(config.get("header1 value3")) == str)
        assert (config.get("header2 value3") == -102 and type(config.get("header2 value3")) == int)
        assert (config.get("misc2") == "binary".encode("utf-8") and type(config.get("misc2")) == bytes)

    def test_default_file_override(self):
        config = configuration.Configuration(
            "tests/test_configurations/default_override.conf",
            "tests/test_configurations/default_configuration.json"
        )
        assert (config.get("header1 value1") == 4 and type(config.get("header1 value1")) == int)
        assert (config.get("header1 value2") == -4203.01 and type(config.get("header1 value2")) == float)  # overriden value
        assert (config.get("header2 value1") == "hello" and type(config.get("header2 value1")) == str)
        assert (config.get("header2 value2") == True and type(config.get("header2 value2")) == bool)
        assert (config.get("misc1") == True and type(config.get("misc1")) == bool)  # overriden value


class MiscTest(unittest.TestCase):
    def test_invalid_datatype(self):
        self.assertRaises(
            configuration.ConfigInvalidDataTypeError,
            configuration.Configuration,
            "tests/test_configurations/invalid_datatype.conf"
        )

    def unknown_file(self):
        self.assertRaises(
            FileNotFoundError,
            configuration.Configuration,
            "tests/test_configurations/non_existent_file.conf"
        )

if __name__ == '__main__':
    unittest.main()
