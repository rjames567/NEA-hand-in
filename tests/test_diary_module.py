import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend/")

import components.diaries

import configuration
import mysql_handler

config = configuration.Configuration(
    "./project_config.conf",
    default_conf_filename="./default_config.json"
)
connection = mysql_handler.Connection(
    user=config.get("mysql username"),
    password=config.get("mysql password"),
    schema=config.get("mysql schema"),
    host=config.get("mysql host")
)

diaries = components.diaries.Diaries(connection)

def add_entries():
    input("Press any key to proceed")
    print("Check add entry")
    diaries.add_entry(3, 3, 4, 2, 4, "Diary entry summary", "Diary entry thoughts", 52)

    input("Press any key to proceed")
    print("Check add entry")
    diaries.add_entry(4, 5, 5, None, None, None, None, 1)

    input("Press any key to proceed")
    print("Check add entry")
    diaries.add_entry(4, 1, 3, 2, None, None, None, 3)

    input("Press any key to proceed")
    print("Check add entry")
    diaries.add_entry(1, 2, 5, None, 5, None, None, 28)

    input("Press any key to proceed")
    print("Check add entry")
    diaries.add_entry(2, 2, 5, 3, 5, None, None, 19)

def delete_entries():
    input("Press any key to proceed")
    print("Check entry removed")
    diaries.delete_entry(1, 1)

    input("Press any key to proceed")
    print("Check no change")
    diaries.delete_entry(5, 1)

    input("Press any key to proceed")
    print("Check no change")
    diaries.delete_entry(1, 10)

class DiariesTest(unittest.TestCase):
    def test_get_entries(self):
        exp = {0: {'entry_id': 1, 'book_id': 1, 'overall_rating': 5, 'character_rating': 3, 'plot_rating': 2, 'summary': 'Summary', 'thoughts': '<p>Thoughts</p>', 'date_added': '12-02-2024', 'pages_read': 10, 'cover_image': '', 'title': 'Book 1', 'author_id': 1, 'author_name': 'Author 1', 'average_rating': 3.5, 'number_ratings': 2}, 1: {'entry_id': 2, 'book_id': 1, 'overall_rating': 1, 'character_rating': 2, 'plot_rating': 5, 'summary': 'Entry summary', 'thoughts': '<p>Entry thoughts</p>', 'date_added': '12-02-2024', 'pages_read': 21, 'cover_image': '', 'title': 'Book 1', 'author_id': 1, 'author_name': 'Author 1', 'average_rating': 3.5, 'number_ratings': 2}, 2: {'entry_id': 3, 'book_id': 2, 'overall_rating': 5, 'character_rating': 3, 'plot_rating': 2, 'summary': 'A summary', 'thoughts': '<p>Thoughts</p>', 'date_added': '12-02-2024', 'pages_read': 11, 'cover_image': '', 'title': 'Book 2', 'author_id': 2, 'author_name': 'Author 2', 'average_rating': 4.0, 'number_ratings': 3}}
        assert (diaries.get_entries(1) == exp)

        exp = {0: {'entry_id': 4, 'book_id': 5, 'overall_rating': 2, 'character_rating': 4, 'plot_rating': 1, 'summary': 'Entry summary', 'thoughts': '<p>Entry thoughts</p>', 'date_added': '12-02-2024', 'pages_read': 2, 'cover_image': '', 'title': 'Book 5', 'author_id': 1, 'author_name': 'Author 1', 'average_rating': 1.0, 'number_ratings': 1}, 1: {'entry_id': 5, 'book_id': 4, 'overall_rating': 4, 'character_rating': 5, 'plot_rating': 3, 'summary': 'Short entry summary', 'thoughts': '<p>Long entry thoughts.</p>', 'date_added': '12-02-2024', 'pages_read': 5, 'cover_image': '', 'title': 'Book 4', 'author_id': 2, 'author_name': 'Author 2', 'average_rating': 2.75, 'number_ratings': 4}}
        assert (diaries.get_entries(2) == exp)

    def test_get_entries_no_entries(self):
        assert (diaries.get_entries(3) == dict())
        assert (diaries.get_entries(4) == dict())

    def test_get_entries_bad_user(self):
        assert (diaries.get_entries(125) == dict())

if __name__ == "__main__":
    add_entries()
    delete_entries()

    input("Press any key to proceed")
    unittest.main()