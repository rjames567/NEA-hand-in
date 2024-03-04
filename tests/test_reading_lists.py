import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend/")

import components.reading_lists
import components.recommendations

import data_structures
import configuration
import mysql_handler

# -----------------------------------------------------------------------------
# Project constants
# -----------------------------------------------------------------------------
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

number_home_summaries = config.get("home number_home_summaries")

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

class ReadingListTest(unittest.TestCase):
    def test_popular(self):
        exp = {0: {'author': 'Author 1', 'title': 'Book 5', 'book_id': 5, 'cover': ''}, 1: {'author': 'Rick Riordan', 'title': 'The Red Pyramid (Kane Chronicles, #1)', 'book_id': 13, 'cover': ''}, 2: {'author': 'Barbara Kingsolver', 'title': 'The Poisonwood Bible', 'book_id': 16, 'cover': ''}, 3: {'author': 'Author 1', 'title': 'Book 1', 'book_id': 1, 'cover': ''}, 4: {'author': 'Author 2', 'title': 'Book 2', 'book_id': 2, 'cover': ''}, 5: {'author': 'Jennifer L. Armentrout', 'title': 'Opal (Lux, #3)', 'book_id': 20, 'cover': ''}}
        assert (reading_lists.get_popular() == exp)

    def test_list_id_valid(self):
        assert (reading_lists.get_list_id("Currently Reading", 1) == 2)
        assert (reading_lists.get_list_id("Have Read", 3) == 9)
        assert (reading_lists.get_list_id("Test List", 1) == 13)

    def test_list_id_valid_user_invalid_name(self):
        self.assertRaises(
            components.reading_lists.ListNotFoundError,
            reading_lists.get_list_id,
            "Random list",
            3
        )

    def test_list_id_invalid_user_valid_name(self):
        self.assertRaises(
            components.reading_lists.ListNotFoundError,
            reading_lists.get_list_id,
            "Have Read",
            100
        )

    def test_get_list_names_valid(self):
        exp = [{'id': 1, 'name': 'Want to Read'}, {'id': 2, 'name': 'Currently Reading'}, {'id': 3, 'name': 'Have Read'}, {'id': 13, 'name': 'Test list'}]
        out = reading_lists.get_names(1)
        assert (out._items == exp and type(out) == data_structures.Queue)

        exp = [{'id': 4, 'name': 'Want to Read'}, {'id': 5, 'name': 'Currently Reading'}, {'id': 6, 'name': 'Have Read'}, {'id': 14, 'name': 'Test list'}]
        out = reading_lists.get_names(2)
        assert (out._items == exp and type(out) == data_structures.Queue)

        exp = [{'id': 7, 'name': 'Want to Read'}, {'id': 8, 'name': 'Currently Reading'}, {'id': 9, 'name': 'Have Read'}]
        out = reading_lists.get_names(3)
        assert (out._items == exp and type(out) == data_structures.Queue)

        exp = [{'id': 10, 'name': 'Want to Read'}, {'id': 11, 'name': 'Currently Reading'}, {'id': 12, 'name': 'Have Read'}]
        out = reading_lists.get_names(4)
        assert (out._items == exp and type(out) == data_structures.Queue)

    def test_get_list_names_invalid(self):
        out = reading_lists.get_names(400)
        assert (out._items == [] and type(out) == data_structures.Queue)

    def test_currently_reading(self):
        exp = [{'author': 'Rick Riordan', 'title': 'The Red Pyramid (Kane Chronicles, #1)', 'book_id': 13, 'cover': ''}]
        assert (reading_lists.get_currently_reading(1) == exp)

        exp = [{'author': 'Barbara Kingsolver', 'title': 'The Poisonwood Bible', 'book_id': 16, 'cover': ''}, {'author': 'Author 1', 'title': 'Book 1', 'book_id': 1, 'cover': ''}]
        assert (reading_lists.get_currently_reading(2) == exp)

        exp = [{'author': 'Author 2', 'title': 'Book 2', 'book_id': 2, 'cover': ''}, {'author': 'Jennifer L. Armentrout', 'title': 'Opal (Lux, #3)', 'book_id': 20, 'cover': ''}, {'author': 'Author 1', 'title': 'Book 5', 'book_id': 5, 'cover': ''}]
        assert (reading_lists.get_currently_reading(3) == exp)

        exp = [{'author': 'Author 1', 'title': 'Book 5', 'book_id': 5, 'cover': ''}]
        assert (reading_lists.get_currently_reading(4) == exp)

        assert (reading_lists.get_currently_reading(5) == [])

    def test_currently_reading_unknown(self):
        assert (reading_lists.get_currently_reading(400) == [])

    def test_want_read(self):
        exp = [{'author': 'Kristin Hannah', 'title': 'The Nightingale', 'book_id': 6, 'cover': ''}, {'author': 'Rick Riordan', 'title': 'The Sea of Monsters (Percy Jackson and the Olympians, #2)', 'book_id': 9, 'cover': ''}]
        assert (reading_lists.get_want_read(1) == exp)

        exp = [{'author': 'Rick Riordan', 'title': 'The Red Pyramid (Kane Chronicles, #1)', 'book_id': 13, 'cover': ''}, {'author': 'Author 3', 'title': 'Animal Farm', 'book_id': 7, 'cover': ''}, {'author': 'Marie Kondo', 'title': 'The Life-Changing Magic of Tidying Up: The Japanese Art of Decluttering and Organizing', 'book_id': 15, 'cover': ''}]
        assert (reading_lists.get_want_read(2) == exp)

        exp = [{'author': 'Author 3', 'title': 'Animal Farm', 'book_id': 7, 'cover': ''}, {'author': 'Mary E. Pearson', 'title': 'The Kiss of Deception (The Remnant Chronicles, #1)', 'book_id': 8, 'cover': ''}]
        assert (reading_lists.get_want_read(3) == exp)

        exp = [{'author': 'Rick Riordan', 'title': 'The Last Olympian (Percy Jackson and the Olympians, #5)', 'book_id': 11, 'cover': ''}, {'author': 'Rick Riordan', 'title': 'The Red Pyramid (Kane Chronicles, #1)', 'book_id': 13, 'cover': ''}, {'author': 'Marie Kondo', 'title': 'The Life-Changing Magic of Tidying Up: The Japanese Art of Decluttering and Organizing', 'book_id': 15, 'cover': ''}, {'author': 'Author 1', 'title': 'Book 1', 'book_id': 1, 'cover': ''}]
        assert (reading_lists.get_want_read(4) == exp)

        assert (reading_lists.get_want_read(5) == [])

    def test_want_read_unknown(self):
        assert (reading_lists.get_want_read (400) == [])

    def test_reading_list_entries(self):
        exp = ({0: {'id': 6, 'cover': '', 'title': 'The Nightingale', 'synopsis': '<p></p>', 'author': 'Kristin Hannah', 'author_id': 4, 'date_added': '14-02-2024', 'genres': ['Genre 1', 'Genre 2', 'Genre 3', 'Genre 4', 'Genre 5', 'Genre 6', 'Genre 7', 'Genre 8'], 'average_rating': 0.0, 'num_reviews': 0}, 1: {'id': 9, 'cover': '', 'title': 'The Sea of Monsters (Percy Jackson and the Olympians, #2)', 'synopsis': '<p></p>', 'author': 'Rick Riordan', 'author_id': 9, 'date_added': '14-02-2024', 'genres': ['Genre 1', 'Genre 2', 'Genre 3', 'Genre 4', 'Genre 5', 'Genre 6', 'Genre 7', 'Genre 8'], 'average_rating': 0.0, 'num_reviews': 0}}, 'Start Reading', 2)
        assert (reading_lists.get_values(1, 1) == exp)

        exp = ({0: {'id': 1, 'cover': '', 'title': 'Book 1', 'synopsis': '<p>This book does not have a synopsis</p>', 'author': 'Author 1', 'author_id': 1, 'date_added': '14-02-2024', 'genres': ['Genre 1', 'Genre 2', 'Genre 3', 'Genre 4', 'Genre 5', 'Genre 6', 'Genre 7', 'Genre 8'], 'average_rating': 3.5, 'num_reviews': 2}, 1: {'id': 3, 'cover': '', 'title': 'Book 3', 'synopsis': '<p>This book does not have a synopsis</p>', 'author': 'Author 3', 'author_id': 3, 'date_added': '14-02-2024', 'genres': ['Genre 1', 'Genre 2', 'Genre 3', 'Genre 4', 'Genre 5', 'Genre 6', 'Genre 7', 'Genre 8'], 'average_rating': 3.0, 'num_reviews': 3}, 2: {'id': 4, 'cover': '', 'title': 'Book 4', 'synopsis': '<p>This book does not have a synopsis</p>', 'author': 'Author 2', 'author_id': 2, 'date_added': '14-02-2024', 'genres': ['Genre 1', 'Genre 2', 'Genre 3', 'Genre 4', 'Genre 5', 'Genre 6', 'Genre 7', 'Genre 8'], 'average_rating': 2.75, 'num_reviews': 4}}, None, None)
        assert (reading_lists.get_values(9, 3) == exp)

        exp = ({0: {'id': 21, 'cover': '', 'title': 'Origin (Lux, #4)', 'synopsis': '<p></p>', 'author': 'Jennifer L. Armentrout', 'author_id': 19, 'date_added': '14-02-2024', 'genres': ['Genre 1', 'Genre 2', 'Genre 3', 'Genre 4', 'Genre 5', 'Genre 6', 'Genre 7', 'Genre 8'], 'average_rating': 0.0, 'num_reviews': 0}}, None, None)
        assert (reading_lists.get_values(13, 1) == exp)

        exp = ({0: {'id': 2, 'cover': '', 'title': 'Book 2', 'synopsis': '<p>This book does not have a synopsis</p>', 'author': 'Author 2', 'author_id': 2, 'date_added': '14-02-2024', 'genres': ['Genre 1', 'Genre 2', 'Genre 3', 'Genre 4', 'Genre 5', 'Genre 6', 'Genre 7', 'Genre 8'], 'average_rating': 4.0, 'num_reviews': 3}, 1: {'id': 3, 'cover': '', 'title': 'Book 3', 'synopsis': '<p>This book does not have a synopsis</p>', 'author': 'Author 3', 'author_id': 3, 'date_added': '14-02-2024', 'genres': ['Genre 1', 'Genre 2', 'Genre 3', 'Genre 4', 'Genre 5', 'Genre 6', 'Genre 7', 'Genre 8'], 'average_rating': 3.0, 'num_reviews': 3}, 2: {'id': 4, 'cover': '', 'title': 'Book 4', 'synopsis': '<p>This book does not have a synopsis</p>', 'author': 'Author 2', 'author_id': 2, 'date_added': '14-02-2024', 'genres': ['Genre 1', 'Genre 2', 'Genre 3', 'Genre 4', 'Genre 5', 'Genre 6', 'Genre 7', 'Genre 8'], 'average_rating': 2.75, 'num_reviews': 4}}, None, None)
        assert (reading_lists.get_values(12, 4) == exp)

        exp = ({}, None, None)
        assert (reading_lists.get_values(14, 2) == exp)

    def test_reading_list_entries_invalid_user(self):
        self.assertRaises(
            components.reading_lists.ListNotFoundError,
            reading_lists.get_values,
            1,
            400
        )

    def test_reading_list_entries_invalid_list(self):
        self.assertRaises(
            components.reading_lists.ListNotFoundError,
            reading_lists.get_values,
            400,
            1
        )

    def test_recent_read(self):
        assert (reading_lists.get_most_recent_read(1) == (1, 'Book 1'))
        assert (reading_lists.get_most_recent_read(2) == (2, 'Book 2'))
        assert (reading_lists.get_most_recent_read(3) == (1, 'Book 1'))
        assert (reading_lists.get_most_recent_read(4) == (2, 'Book 2'))
        assert (reading_lists.get_most_recent_read(5) is None)

    def test_recent_addition(self):
        assert (reading_lists.get_newest_addition(1) == (6, 'The Nightingale'))
        assert (reading_lists.get_newest_addition(2) == (13, 'The Red Pyramid (Kane Chronicles, #1)'))
        assert (reading_lists.get_newest_addition(3) == (7, 'Animal Farm'))
        assert (reading_lists.get_newest_addition(4) == (11, 'The Last Olympian (Percy Jackson and the Olympians, #5)'))
        assert (reading_lists.get_newest_addition(5) is None)

def add_entry():
    input("Press enter to proceed")
    print("Check addition of book 1 to list ID 1")
    reading_lists.add_entry(1, 1, 1)

    input("Press enter to proceed")
    print("Check no change")
    reading_lists.add_entry(1, 4, 1)

    input("Press enter to proceed")
    print("Check no change")
    reading_lists.add_entry(1, 1, 400)

    input("Press enter to proceed")
    print("Check no change")
    reading_lists.add_entry(400, 1, 1)

def remove_entry():
    input("Press enter to proceed (temp insert)")
    reading_lists.add_entry(1, 1, 1)
    input("Press enter to proceed")
    print("Check removal of book 1 to list ID 1")
    reading_lists.remove_entry(1, 1, 1)

    input("Press enter to proceed")
    print("Check no change")
    reading_lists.remove_entry(1, 1, 400)

    input("Press enter to proceed")
    print("Check no change")
    reading_lists.remove_entry(1, 4, 1)

def remove_list():
    input("Press enter to proceed")
    print("Check removal of list ID 1")
    reading_lists.remove_list(1, 1)

    input("Press enter to proceed")
    print("Check no change")
    reading_lists.remove_list(2, 2)

    input("Press enter to proceed")
    print("Check no change")
    reading_lists.remove_list(400, 400)

def add_list():
    input("Press enter to proceed")
    print("Check add of new list name")
    reading_lists.create_list(3, "Testing list name")

if __name__ == "__main__":
    add_entry()
    remove_entry()
    remove_list()
    add_list()

    input("Press enter to proceed")
    unittest.main()