import sys
import os

sys.path.append("/".join(os.getcwd().split("/")[:-1]) + "/backend/")

import logger

def test_log_start():
    print("Check header in file")
    return logger.Logging(filepath="", debugging=True)

def test_log_write_debugging(log):
    input("Press any key to proceed")
    print("Check addition of message")
    log.output_message("Test message")

def test_log_write_linewrap(log):
    input("Press any key to proceed")
    print("Check addition of message")
    log.output_message("This is a very long test message. It should be long enough to wrap around lines in the log file. This message should demonstrate this ability clearly.")

def test_log_write():
    input("Press any key to proceed")
    print("Check no change to log")
    log = logger.Logging(filepath="", debugging=False)
    log.output_message("Test message")

if __name__ == "__main__":
    log = test_log_start()
    test_log_write_debugging(log)
    test_log_write_linewrap(log)
    test_log_write()