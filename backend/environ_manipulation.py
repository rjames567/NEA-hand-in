# ------------------------------------------------------------------------------
# Standard Python library imports
# ------------------------------------------------------------------------------
import re


# ------------------------------------------------------------------------------
# Application manipulation
# ------------------------------------------------------------------------------
class application:
    def get_target(environ):
        path = environ["REQUEST_URI"]
        temp = re.match("/[\w-]+/([\w-]+)", path)  # Should not include dashes in result, but included, so it does
        # not break if it does.
        if temp:
            return temp.group(1)
        return None

    def get_sub_target(environ):
        path = environ["REQUEST_URI"]
        temp = re.match("/[\w-]+/[\w-]+/([\w-]+)", path)  # Should not
        # include dashes in result, but included, so it does not break if it
        # does.
        if temp:
            return temp.group(1)
        return None
