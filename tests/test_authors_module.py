import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend/")

import configuration
import mysql_handler
import components.authors

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

authors = components.authors.Authors(
    connection,
    config.get("number_display_genres"),
    config.get("home number_home_summaries")
)


class AuthorsTest(unittest.TestCase):
    def test_number_followers(self):
        assert (authors.get_number_followers(1) == 2)
        assert (authors.get_number_followers(2) == 3)
        assert (authors.get_number_followers(3) == 0)

    def test_get_about_data_valid(self):
        out = authors.get_about_data(1)
        out["genres"] = set(out["genres"])
        exp = {
            "name": "Author 1",
            "about": "<p>This is the first author's about.</p>",
            "author_id": 1,
            "num_followers": 2,
            "books": [
                {"id": 1, "title": "Book 1", "cover": ""},
                {"id": 5, "title": "Book 5", "cover": ""}
            ],
            "average_rating": 2.67,
            "num_ratings": 3,
            "genres": set(['Genre 8', 'Genre 1', 'Genre 9', 'Genre 4', 'Genre 2', 'Genre 7'])
            # uses sets so order can be ignored.
        }
        assert (out == exp)

        out = authors.get_about_data(2)
        out["genres"] = set(out["genres"])
        exp = {
            "name": "Author 2",
            "about": "<p>This is the second author's about.</p>",
            "author_id": 2,
            "num_followers": 3,
            "books": [
                {"id": 2, "title": "Book 2", "cover": ""},
                {"id": 4, "title": "Book 4", "cover": ""}
            ],
            "average_rating": 3.29,
            "num_ratings": 7,
            "genres": set(['Genre 8', 'Genre 5', 'Genre 3', 'Genre 10', 'Genre 1', 'Genre 2'])
            # uses sets so order can be ignored.
        }
        assert (out == exp)

        out = authors.get_about_data(3)
        out["genres"] = set(out["genres"])
        exp = {
            "name": "Author 3",
            "about": "<p>This is the third author's about.</p>",
            "author_id": 3,
            "num_followers": 0,
            "books": [
                {"id": 3, "title": "Book 3", "cover": ""}
            ],
            "average_rating": 3.0,
            "num_ratings": 3,
            "genres": set(['Genre 9', 'Genre 6', 'Genre 8', 'Genre 5', 'Genre 10', 'Genre 3', 'Genre 4', 'Genre 2'])
            # uses sets so order can be ignored.
        }
        assert (out == exp)

    def test_get_about_data_invalid(self):
        self.assertRaises(
            components.authors.AuthorNotFoundError,
            authors.get_about_data,
            23
        )

    def test_get_author_id_list(self):
        assert (set(authors.get_author_id_list()) == set([1,2,3]))

    def test_get_author_name_list(self):
        exp = [
            {"id": 1, "name": "Author 1"},
            {"id": 2, "name": "Author 2"},
            {"id": 3, "name": "Author 3"}
        ]

        assert (authors.get_author_id_list(True) == exp)

    def test_author_follower_books_valid(self):
        exp = {
            0: {"author": "Author 2", "title": "Book 2", "book_id": 2, "cover": ""},
            1: {"author": "Author 1", "title": "Book 1", "book_id": 1, "cover": ""},
            2: {"author": "Author 2", "title": "Book 4", "book_id": 4, "cover": ""},
            3: {"author": "Author 1", "title": "Book 5", "book_id": 5, "cover": ""}
        }

        assert (exp == authors.get_author_favourite_data(1))

        exp = {
            0: {"author": "Author 2", "title": "Book 2", "book_id": 2, "cover": ""},
            1: {"author": "Author 1", "title": "Book 1", "book_id": 1, "cover": ""},
            2: {"author": "Author 2", "title": "Book 4", "book_id": 4, "cover": ""},
            3: {"author": "Author 1", "title": "Book 5", "book_id": 5, "cover": ""}
        }

        assert (exp == authors.get_author_favourite_data(2))

        exp = {
            0: {"author": "Author 2", "title": "Book 2", "book_id": 2, "cover": ""},
            1: {"author": "Author 2", "title": "Book 4", "book_id": 4, "cover": ""}
        }

        assert (exp == authors.get_author_favourite_data(3))

    def test_author_follower_books_invalid_user(self):
        assert (authors.get_author_favourite_data(40) == None)

    def test_author_follower_books_no_following(self):
        assert (authors.get_author_favourite_data(4) == None)


def test_follow_author_valid():
    input("Press any key to proceed")
    print("check addition for follow between user 4, author 1 in author_followers table")
    authors.follow(4, 1)

def test_follow_author_invalid_user():
    input("Press any key to proceed")
    print("Check no change to author_followers table")
    authors.follow(500, 1)

def test_follow_author_invalid_author():
    input("Press any key to proceed")
    print("Check no change to author_followers table")
    authors.follow(1, 500)

def test_unfollow_author_valid():
    input("Press any key to proceed")
    print("Check removal of follow between author 1 and user 1 from author_followers table")
    authors.unfollow(1, 1)

def test_unfollow_author_invalid_user_not_follow():
    input("Press any key to proceed")
    print("Check no change to author_followers table")
    authors.unfollow(1, 3)

def test_unfollow_author_invalid_user():
    input("Press any key to proceed")
    print("Check no change to author_followers table")
    authors.unfollow(100, 1)

def test_unfollow_author_invalid_author():
    input("Press any key to proceed")
    print("Check no change to author_followers table")
    authors.unfollow(1, 100)


if __name__ == "__main__":
    test_follow_author_valid()
    test_follow_author_invalid_user()
    test_follow_author_invalid_author()
    test_unfollow_author_valid()
    test_unfollow_author_invalid_user_not_follow()
    test_unfollow_author_invalid_user()
    test_unfollow_author_invalid_author()

    unittest.main()