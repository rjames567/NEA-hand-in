# ------------------------------------------------------------------------------
# Standard Python library imports
# ------------------------------------------------------------------------------
import datetime
import json


# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
class Logging:
    def __init__(self, debugging=False, filepath="/tmp/", clear=True, line_length=150):
        self._debugging = debugging
        self._line_length = line_length
        self._filepath = filepath
        self._clear = clear
        self._open()

    def _open(self):
        if self._debugging:
            if self._clear:
                self._method = "w+"
                start = ""
            else:
                self._method = "a+"
                start = "\n\n"

            now = datetime.datetime.now()
            start += ("-" * self._line_length) + "\nNew session created: "
            start += now.strftime("%d-%m-%Y %H:%M:%S") + "\n" + ("-" * self._line_length) + "\n"

            self._write(start)
            self._method = "a+"

    def _write(self, message):
        if type(message) == list:
            message = f"[{','.join(message)}]"
        elif type(message) == dict:
            message = json.dumps(message)
        elif type(message) != str:
            message = str(message) # Make it easier to write too – and faster if it is not in debugging mode as
            # conversions do not need to be made
        with open(self._filepath + "output.log", self._method) as f:
            f.write(message)

    def output_message(self, message):
        if self._debugging:
            message = str(message)
            now = datetime.datetime.now()
            string = "[" + now.strftime("%d-%m-%Y %H:%M:%S") + "] "
            length = len(string)
            new_message = [message[i:i + (self._line_length - length)] for i in range(0, len(message), self._line_length - length)]
            string += ("\n" + " " * length).join(new_message) + "\n"
            self._write(string)
