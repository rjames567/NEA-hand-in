# -----------------------------------------------------------------------------
# Standard Python library imports
# -----------------------------------------------------------------------------
import datetime
import hashlib
import secrets
import time


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------
class SessionExpiredError(Exception):
    def __init__(self, session_id):
        message = f"Session id '{session_id}' has expired"
        super().__init__(message)


class UserExistsError(Exception):
    def __init__(self, username):
        message = f"User already exists with the username {username}."
        super().__init__(message)


class InvalidUserCredentialsError(Exception):
    def __init__(self, username):
        message = f"Incorrect username or password entered for {username}"
        super().__init__(message)


# -----------------------------------------------------------------------------
# Objects
# -----------------------------------------------------------------------------
class Accounts:
    def __init__(self, connection, hashing_algorithm, hashing_salt, number_hash_passes, reading_lists):
        self._hashing_algorithm = hashing_algorithm
        self._hashing_salt = hashing_salt
        self._number_hash_passes = number_hash_passes
        self._connection = connection
        self._reading_lists = reading_lists
    
    def hash_password(self, password):
        result = hashlib.pbkdf2_hmac(
            self._hashing_algorithm,
            password.encode("utf-8"),  # Needs to be in binary
            self._hashing_salt,  # Salt needs to be in binary - stored as binary in config
            self._number_hash_passes  # Recommended number of passes is 100,000
        )

        return result.hex()  # Hash is returned as a hex string, so converts back

    def check_credentials(self, username, password):
        entered_password = self.hash_password(password)
        query_result = self._connection.query(
            """
            SELECT password_hash, user_id FROM users
            WHERE username="{}";
            """.format(username)
        )

        if (len(query_result) == 0) or (query_result[0][0] != entered_password):
            raise InvalidUserCredentialsError(username)
        else:
            return query_result[0][1]

    def create_user(self, first_name, surname, username, password):
        query_result = self._connection.query(
            """
            SELECT username FROM users
            WHERE username="{}"
            """.format(username)
        )

        if len(query_result):
            raise UserExistsError(username)
        else:
            self._connection.query(
                """
                INSERT INTO users (first_name, surname, username, password_hash)
                VALUES ("{first_name}", "{surname}", "{username}", "{password}");
                """.format(
                    first_name=first_name,
                    surname=surname,
                    username=username,
                    password=self.hash_password(password)  # Password must be hashed before
                    # storing in the database.
                )
            )

            user_id = self.get_user_id(username)

            self._reading_lists.create_list(user_id, "Want to Read")
            self._reading_lists.create_list(user_id, "Currently Reading")
            self._reading_lists.create_list(user_id, "Have Read")

            return user_id

    def get_user_id(self, username):
        query_result = self._connection.query(
            """
            SELECT user_id FROM users
            WHERE username="{}";
            """.format(username)
        )

        return query_result[0][0]
    
    def get_user_id_list(self):
        res = self._connection.query("SELECT user_id FROM users")
        return [i[0] for i in res]


class Sessions:
    def __init__(self, connection, token_size):
        self._connection = connection
        self._token_size = token_size

    def create_session(self, user_id):
        token = secrets.token_bytes(self._token_size).hex() + str(time.time()).split(".")[0]
        # the time to make it shorter
        # Generates a random string, and adds time to reduce required size of
        # the randomly generated string for speed.
        # https://docs.python.org/3/library/secrets.html

        # Probability of getting duplicates is very low, and gets lower as the
        # size of the string increases. It would also need to be within 1
        # second, as time.time() is added to the end which is the number of
        # seconds since the epoch.

        self._connection.query(
            """
            INSERT INTO sessions (client_id, user_id) VALUES ("{token}", {user_id});
            """.format(token=token, user_id=user_id)
        )

        return token

    def update_time(self, session_id):
        self._connection.query(
            """
            UPDATE sessions
            SET
                date_added=NOW()
            WHERE client_id="{}";
            """.format(session_id)
        )

    def get_user_id(self, session_id):
        res = self._connection.query(
            """
            SELECT user_id, date_added FROM sessions
            WHERE client_id="{}";
            """.format(session_id)
        )
        if len(res) == 0:
            raise SessionExpiredError(session_id)  # If there is no entries
            # it must have been deleted by a maintenance script, as it had
            # expired.
        else:
            res = res[0]  # Gets first element result from list - should only be
            # one result
        expiry_datetime = res[1] + datetime.timedelta(days=7)
        # Set expiry date to one day after it has been last used

        if datetime.datetime.now() > expiry_datetime:
            self.close(session_id)
            raise SessionExpiredError(session_id)
        else:
            return res[0]

        # Does not update the session time - Excluded from this as any request
        # from the client indicates that is still active, regardless of whether
        # the user id is needed to carry out the required process.

    def close(self, session_id):
        self._connection.query(
            """
            DELETE FROM sessions
            WHERE client_id="{}";
            """.format(session_id)
        )
    
    def get_session_id_list(self):
        return [i[0] for i in self._connection.query("SELECT client_id FROM sessions")]
