import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend/")

import configuration
import mysql_handler
import components.recommendations
import components.accounts
import components.reading_lists

config = configuration.Configuration(
    "./project_config.conf",
    default_conf_filename="./default_config.json"
)
# The json does not need to be user editable, so is not very readable.

connection = mysql_handler.Connection(
    user=config.get("mysql username"),
    password=config.get("mysql password"),
    schema=config.get("mysql schema"),
    host=config.get("mysql host")
)

number_home_summaries = config.get("home number_home_summaries")

sessions = components.accounts.Sessions(
    connection,
    config.get("session_id_length")
)
recommendations = components.recommendations.Recommendations(
    connection,
    config.get("recommendations number_converge_iterations"),
    config.get("recommendations hyperparameter"),
    config.get("number_display_genres"),
    config.get("recommendations inital_recommendation_matrix_value"),
    config.get("recommendations reading_list_percentage_increase"),
    config.get("recommendations author_following_percentage_increase"),
    config.get("recommendations bad_recommendations_matrix_value"),
    config.get("recommendations minimum_required_reviews"),
    config.get("recommendations number_recommendations"),
)
reading_lists = components.reading_lists.ReadingLists(
    connection,
    number_home_summaries,
    config.get("number_display_genres"),
    recommendations
)
accounts = components.accounts.Accounts(
    connection,
    config.get("passwords hashing_algorithm"),
    config.get("passwords salt"),  # Stored in the config as binary
    config.get("passwords number_hash_passes"),
    reading_lists
)


class AccountsTest(unittest.TestCase):
    def test_user_id(self):
        assert (accounts.get_user_id("user1") == 1)
        assert (accounts.get_user_id("user2") == 2)
        assert (accounts.get_user_id("user3") == 3)
        assert (accounts.get_user_id("user4") == 4)

    def test_user_id_unknown(self):
        self.assertRaises(
            IndexError,
            accounts.get_user_id,
            "adasdasdasd"
        )

    def test_create_account_username_taken(self):
        self.assertRaises(
            components.accounts.UserExistsError,
            accounts.create_user,
            "user",
            "4",
            "user4",
            "password"
        )

    def test_password_hash(self):
        assert (accounts.hash_password("password") == "5d557544916fde5c6b162cfcbce84181fb2cbe8798439b643edf96ee4c5826b4")
        assert (accounts.hash_password("hello world") == "0180e034766b1dbd247e527dedd6b6d04795e3ad5e9752444d6d785ae525ee84")
        assert (accounts.hash_password("T3st Passw0rd!") == "4b9f7c53850304f5fe3fb3014d1a331dc2df1195a443b1d714e62e36ef870cf1")

    def test_check_credentials_valid(self):
        assert (accounts.check_credentials("user1", "password") == 1)
        assert (accounts.check_credentials("user2", "password") == 2)
        assert (accounts.check_credentials("user3", "password") == 3)
        assert (accounts.check_credentials("user4", "password") == 4)

    def test_check_credentials_invalid_username(self):
        self.assertRaises(
            components.accounts.InvalidUserCredentialsError,
            accounts.check_credentials,
            "asdassdjasjdsfbdsf",
            "asdasdsd"
        )

    def test_check_credentials_invalid_password(self):
        self.assertRaises(
            components.accounts.InvalidUserCredentialsError,
            accounts.check_credentials,
            "user1",
            "adasda"
        )

class SessionsTest(unittest.TestCase):
    def test_user_id_valid(self):
        assert (sessions.get_user_id("asdhjaksnce1263872613") == 1)
        assert (sessions.get_user_id("adqweqiueqw0812309812") == 1)
        assert (sessions.get_user_id("zxmcabvzxcn1231231235") == 1)
        assert (sessions.get_user_id("poipoqwerwrw983453453") == 3)

    def test_user_id_unknown(self):
        self.assertRaises(
            components.accounts.SessionExpiredError,
            sessions.get_user_id,
            "unknown_session_id"
        )

def test_user_account_creation():
    print("Check addition of user 5 to users table and system-defined reading lists to reading_list_names table")
    accounts.create_user(
        "user",
        "5",
        "user5",
        "random_password!"
    )

def test_create_session_id():
    input("Press any key to proceed")
    print("Check of new session ID for user 2 to sessions table")
    sessions.create_session(2)

def test_update_session_id_expiry_valid():
    input("Press any key to proceed")
    print("Check update of session expiry time for asdhjaksnce1263872613 session in sessions table")
    sessions.update_time("asdhjaksnce1263872613")

def test_update_session_id_expiry_unknown():
    input("Press any key to proceed")
    print("Check no change to sessions table")
    sessions.update_time("random_session_id")

def test_get_user_id_from_expired():
    input("Press any key to proceed")
    print("Check removal of session sdfasdvnjtit987652678 from sessions table")
    try:
        sessions.get_user_id("sdfasdvnjtit987652678")
        print("    Error throw failed")
    except components.accounts.SessionExpiredError:
        print("    Error throw succeed")

def test_close_session():
    input("Press any key to proceed")
    print("Check removal of swcdecwftrbr132788943 session from sessions table")
    sessions.close("swcdecwftrbr132788943")

def test_close_session_unknown():
    input("Press any key to proceed")
    print("Check no change to sessions table")
    sessions.close("unknown_session")


if __name__ == '__main__':
    test_user_account_creation()
    test_create_session_id()
    test_update_session_id_expiry_valid()
    test_update_session_id_expiry_unknown()
    test_get_user_id_from_expired()
    test_close_session()
    test_close_session_unknown()

    unittest.main()