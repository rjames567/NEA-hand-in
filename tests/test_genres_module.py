import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend/")

import components.genres
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

genres = components.genres.Genres(connection)

class GenresTest(unittest.TestCase):
    def test_about_data(self):
        exp = {'name': 'Genre 1', 'about': '<p>This genre does not have an about</p>', 'books': {0: {'id': 4, 'title': 'Book 4', 'author': 'Author 2', 'cover': ''}}}
        assert (genres.get_about_data("Genre 1") == exp)

        exp = {'name': 'Genre 2', 'about': '<p>This genre does not have an about</p>', 'books': {0: {'id': 4, 'title': 'Book 4', 'author': 'Author 2', 'cover': ''}}}
        assert (genres.get_about_data("Genre 2") == exp)

        exp = {'name': 'Genre 3', 'about': '<p>This genre does not have an about</p>', 'books': {0: {'id': 3, 'title': 'Book 3', 'author': 'Author 3', 'cover': ''}}}
        assert (genres.get_about_data("Genre 3") == exp)

        exp = {'name': 'Genre 4', 'about': '<p>This genre does not have an about</p>', 'books': {0: {'id': 3, 'title': 'Book 3', 'author': 'Author 3', 'cover': ''}}}
        assert (genres.get_about_data("Genre 4") == exp)

        exp = {'name': 'Genre 5', 'about': '<p>This genre does not have an about</p>', 'books': {0: {'id': 4, 'title': 'Book 4', 'author': 'Author 2', 'cover': ''}}}
        assert (genres.get_about_data("Genre 5") == exp)

        exp = {'name': 'Genre 6', 'about': '<p>This genre does not have an about</p>', 'books': {0: {'id': 3, 'title': 'Book 3', 'author': 'Author 3', 'cover': ''}}}
        assert (genres.get_about_data("Genre 6") == exp)

        exp = {'name': 'Genre 7', 'about': '<p>This genre does not have an about</p>', 'books': {0: {'id': 1, 'title': 'Book 1', 'author': 'Author 1', 'cover': ''}}}
        assert (genres.get_about_data("Genre 7") == exp)

        exp = {'name': 'Genre 8', 'about': '<p>This genre does not have an about</p>', 'books': {0: {'id': 1, 'title': 'Book 1', 'author': 'Author 1', 'cover': ''}}}
        assert (genres.get_about_data("Genre 8") == exp)

        exp = {'name': 'Genre 9', 'about': '<p>This genre does not have an about</p>', 'books': {0: {'id': 5, 'title': 'Book 5', 'author': 'Author 1', 'cover': ''}}}
        assert (genres.get_about_data("Genre 9") == exp)

        exp = {'name': 'Genre 10', 'about': '<p>This genre does not have an about</p>', 'books': {0: {'id': 3, 'title': 'Book 3', 'author': 'Author 3', 'cover': ''}}}
        assert (genres.get_about_data("Genre 10") == exp)

    def test_about_unknown(self):
        self.assertRaises(
            components.genres.GenreNotFoundError,
            genres.get_about_data,
            "Genre 100"
        )

    def test_genre_from_id(self):
        assert (genres.id_to_name(1) == "Genre 1")
        assert (genres.id_to_name(2) == "Genre 2")
        assert (genres.id_to_name(3) == "Genre 3")
        assert (genres.id_to_name(4) == "Genre 4")
        assert (genres.id_to_name(5) == "Genre 5")
        assert (genres.id_to_name(6) == "Genre 6")
        assert (genres.id_to_name(7) == "Genre 7")
        assert (genres.id_to_name(8) == "Genre 8")
        assert (genres.id_to_name(9) == "Genre 9")
        assert (genres.id_to_name(10) == "Genre 10")

    def test_genre_from_id_unknown(self):
        self.assertRaises(
            components.genres.GenreNotFoundError,
            genres.id_to_name,
            100
        )

if __name__ == "__main__":
    unittest.main()