import time
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend/")

import configuration
import mysql_handler
import components.recommendations
import components.reading_lists
import components.books

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
books = components.books.Books(
    connection,
    reading_lists,
    config.get("home number_about_similarities"),
    number_home_summaries,
    config.get("number_display_genres")
)

def test_leave_review():
    input("Press any key to proceed")
    print("check addition for review for book 1, user 2.")
    books.leave_review(2, 1, 5, 3, 2, "This is the review summary", "This is the main review body.")

    input("Press any key to proceed")
    print("check addition for review for book 1, user 4.")
    books.leave_review(4, 1, 4, None, None, None, None)

    input("Press any key to proceed")
    print("check addition for review for book 2, user 3.")
    books.leave_review(3, 2, 3, None, 2, None, None)

    input("Press any key to proceed")
    print("check addition for review for book 3, user 1.")
    books.leave_review(1, 3, 3, 3, None, None, None)

    input("Press any key to proceed")
    print("check addition for review for book 5, user 2.")
    books.leave_review(2, 5, 3, 3, 2, None, None)

def test_leave_review_existing():
    input("Press any key to proceed")
    print("check addition for review for book 1, user 1, and removal of old review")
    books.leave_review(1, 1, 3, 3, 2, "summary", "main")

def test_remove_review_valid():
    input("Press any key to proceed")
    print("add review")
    books.leave_review(2, 5, 5, 5, 5, None, None)
    input("Press any key to proceed (delete review) check removal of review")
    books.delete_review(14, 2)

def test_remove_review_invalid_bad_review():
    input("Press any key to proceed")
    print("add review")
    books.leave_review(2, 5, 5, 5, 5, None, None)
    input("Press any key to proceed (delete review) check no change")
    books.delete_review(50, 2)

def test_remove_review_invalid_bad_user():
    input("Press any key to proceed")
    print("add review")
    books.leave_review(2, 5, 5, 5, 5, None, None)
    input("Press any key to proceed (delete review) check no change")
    books.delete_review(14, 5895)


class BooksTest(unittest.TestCase):
    def test_similar_books(self):
        exp = [{'author': 'Author 1', 'title': 'Book 5', 'book_id': 5, 'cover': ''}, {'author': 'Author 2', 'title': 'Book 2', 'book_id': 2, 'cover': ''}]
        assert (books.get_similar_items(1) == exp)

        exp = [{'author': 'Author 2', 'title': 'Book 4', 'book_id': 4, 'cover': ''}, {'author': 'Author 3', 'title': 'Book 3', 'book_id': 3, 'cover': ''}]
        assert (books.get_similar_items(2) == exp)

        exp = [{'author': 'Author 1', 'title': 'Book 5', 'book_id': 5, 'cover': ''}, {'author': 'Author 2', 'title': 'Book 2', 'book_id': 2, 'cover': ''}]
        assert (books.get_similar_items(3) == exp)

        exp = [{'author': 'Author 1', 'title': 'Book 5', 'book_id': 5, 'cover': ''}, {'author': 'Author 2', 'title': 'Book 2', 'book_id': 2, 'cover': ''}]
        assert (books.get_similar_items(4) == exp)

        exp = [{'author': 'Author 3', 'title': 'Book 3', 'book_id': 3, 'cover': ''}, {'author': 'Author 2', 'title': 'Book 4', 'book_id': 4, 'cover': ''}]
        assert (books.get_similar_items(5) == exp)

    def test_similar_books_unknown_book(self):
        self.assertRaises(
            components.books.BookNotFoundError,
            books.get_similar_items,
            500
        )

    def test_summary_data_id(self):
        exp = {'author': 'Author 1', 'title': 'Book 1', 'book_id': 1, 'cover': ''}
        assert (books.get_summary(1) == exp)

        exp = {'author': 'Author 2', 'title': 'Book 2', 'book_id': 2, 'cover': ''}
        assert (books.get_summary(2) == exp)

        exp = {'author': 'Author 3', 'title': 'Book 3', 'book_id': 3, 'cover': ''}
        assert (books.get_summary(3) == exp)

        exp = {'author': 'Author 2', 'title': 'Book 4', 'book_id': 4, 'cover': ''}
        assert (books.get_summary(4) == exp)

        exp = {'author': 'Author 1', 'title': 'Book 5', 'book_id': 5, 'cover': ''}
        assert (books.get_summary(5) == exp)

    def test_summary_data_id_unknown(self):
        self.assertRaises(
            components.books.BookNotFoundError,
            books.get_summary,
            500
        )

    def test_summary_data_isbn(self):
        exp = {'author': 'Author 1', 'title': 'Book 1', 'book_id': 1, 'cover': ''}
        assert (books.get_summary(isbn="0111111111") == exp)

        exp = {'author': 'Author 2', 'title': 'Book 2', 'book_id': 2, 'cover': ''}
        assert (books.get_summary(isbn="0222222222") == exp)

        exp = {'author': 'Author 3', 'title': 'Book 3', 'book_id': 3, 'cover': ''}
        assert (books.get_summary(isbn="0333333333") == exp)

        exp = {'author': 'Author 2', 'title': 'Book 4', 'book_id': 4, 'cover': ''}
        assert (books.get_summary(isbn="0444444444") == exp)

        exp = {'author': 'Author 1', 'title': 'Book 5', 'book_id': 5, 'cover': ''}
        assert (books.get_summary(isbn="0555555555") == exp)

    def test_summary_data_isbn_unknown(self):
        self.assertRaises(
            components.books.BookNotFoundError,
            books.get_summary,
            isbn="1111111111"
        )

    def test_newest_books(self):
        connection.query("""
            INSERT INTO books (author_id, title, clean_title, synopsis, cover_image, purchase_link, fiction, release_date, isbn) VALUES
            (1, "temp 1", "", "", "", "", 1, "2022-2-2", "1234567890");
        """)
        time.sleep(1.5)

        connection.query("""
            INSERT INTO books (author_id, title, clean_title, synopsis, cover_image, purchase_link, fiction, release_date, isbn) VALUES
            (1, "temp 2", "", "", "", "", 1, "2022-2-2", "1234567890");
        """)
        time.sleep(1.5)


        connection.query("""
            INSERT INTO books (author_id, title, clean_title, synopsis, cover_image, purchase_link, fiction, release_date, isbn) VALUES
            (1, "temp 3", "", "", "", "", 1, "2022-2-2", "1234567890");
        """)
        time.sleep(1.5)

        connection.query("""
            INSERT INTO books (author_id, title, clean_title, synopsis, cover_image, purchase_link, fiction, release_date, isbn) VALUES
            (2, "temp 4", "", "", "", "", 1, "2022-2-2", "1234567890");
        """)
        time.sleep(1.5)

        connection.query("""
            INSERT INTO books (author_id, title, clean_title, synopsis, cover_image, purchase_link, fiction, release_date, isbn) VALUES
            (3, "temp 5", "", "", "", "", 1, "2022-2-2", "1234567890");
        """)
        time.sleep(1.5)

        connection.query("""
            INSERT INTO books (author_id, title, clean_title, synopsis, cover_image, purchase_link, fiction, release_date, isbn) VALUES
            (1, "temp 6", "", "", "", "", 1, "2022-2-2", "1234567890");
        """)
        time.sleep(1.5)

        connection.query("""
            INSERT INTO books (author_id, title, clean_title, synopsis, cover_image, purchase_link, fiction, release_date, isbn) VALUES
            (2, "temp 7", "", "", "", "", 1, "2022-2-2", "1234567890");
        """)
        time.sleep(1.5)

        connection.query("""
            INSERT INTO books (author_id, title, clean_title, synopsis, cover_image, purchase_link, fiction, release_date, isbn) VALUES
            (3, "temp 8", "", "", "", "", 1, "2022-2-2", "1234567890");
        """)

        exp = {
            0: {'author': 'Author 3', 'title': 'temp 8', 'book_id': 13, 'cover': ''},
            1: {'author': 'Author 2', 'title': 'temp 7', 'book_id': 12, 'cover': ''},
            2: {'author': 'Author 1', 'title': 'temp 6', 'book_id': 11, 'cover': ''},
            3: {'author': 'Author 3', 'title': 'temp 5', 'book_id': 10, 'cover': ''},
            4: {'author': 'Author 2', 'title': 'temp 4', 'book_id': 9, 'cover': ''},
            5: {'author': 'Author 1', 'title': 'temp 3', 'book_id': 8, 'cover': ''},
            6: {'author': 'Author 1', 'title': 'temp 2', 'book_id': 7, 'cover': ''},
            7: {'author': 'Author 1', 'title': 'temp 1', 'book_id': 6, 'cover': ''}
        }

        assert (books.get_newest() == exp)

        connection.query("DELETE FROM books WHERE title LIKE 'temp%'")

    def test_get_about_data(self):
        exp = {'title': 'Book 1', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'purchase_link': '', 'release_date': '02/02/2022', 'isbn': '0111111111', 'author': 'Author 1', 'author_about': "<p>This is the first author's about.</p>", 'author_number_followers': 2, 'num_want_read': 0, 'num_reading': 0, 'num_read': 2, 'genres': ['Genre 8', 'Genre 9', 'Genre 4', 'Genre 7', 'Genre 5', 'Genre 2', 'Genre 1', 'Genre 10'], 'author_id': 1, 'average_rating': 3.5, 'num_ratings': 2, 'num_5_stars': 1, 'num_4_stars': 0, 'num_3_stars': 0, 'num_2_stars': 1, 'num_1_star': 0, 'current_user_review': {'review_id': 1, 'overall_rating': 5, 'plot_rating': 5, 'character_rating': 5, 'summary': None, 'rating_body': None}, 'author_following': True, 'reviews': [{'id': 2, 'overall_rating': 2, 'plot_rating': 3, 'character_rating': 1, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user3'}]}
        assert (books.get_about_data(1, 1) == exp)

        exp = {'title': 'Book 2', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'purchase_link': '', 'release_date': '02/02/2022', 'isbn': '0222222222', 'author': 'Author 2', 'author_about': "<p>This is the second author's about.</p>", 'author_number_followers': 3, 'num_want_read': 0, 'num_reading': 0, 'num_read': 3, 'genres': ['Genre 2', 'Genre 3', 'Genre 8', 'Genre 10', 'Genre 5', 'Genre 4', 'Genre 6', 'Genre 7'], 'author_id': 2, 'average_rating': 4.0, 'num_ratings': 3, 'num_5_stars': 1, 'num_4_stars': 1, 'num_3_stars': 1, 'num_2_stars': 0, 'num_1_star': 0, 'current_user_review': {'review_id': 3, 'overall_rating': 3, 'plot_rating': 2, 'character_rating': 3, 'summary': None, 'rating_body': None}, 'author_following': True, 'reviews': [{'id': 5, 'overall_rating': 4, 'plot_rating': 3, 'character_rating': 4, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user4'}, {'id': 4, 'overall_rating': 5, 'plot_rating': 2, 'character_rating': 5, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user2'}]}
        assert (books.get_about_data(2, 1) == exp)

        exp = {'title': 'Book 3', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'purchase_link': '', 'release_date': '02/02/2022', 'isbn': '0333333333', 'author': 'Author 3', 'author_about': "<p>This is the third author's about.</p>", 'author_number_followers': 0, 'num_want_read': 0, 'num_reading': 0, 'num_read': 3, 'genres': ['Genre 4', 'Genre 3', 'Genre 2', 'Genre 6', 'Genre 10', 'Genre 9', 'Genre 8', 'Genre 5'], 'author_id': 3, 'average_rating': 3.0, 'num_ratings': 3, 'num_5_stars': 1, 'num_4_stars': 0, 'num_3_stars': 1, 'num_2_stars': 0, 'num_1_star': 1, 'current_user_review': None, 'author_following': False, 'reviews': [{'id': 8, 'overall_rating': 3, 'plot_rating': 2, 'character_rating': 4, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user4'}, {'id': 7, 'overall_rating': 1, 'plot_rating': 1, 'character_rating': 2, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user3'}, {'id': 6, 'overall_rating': 5, 'plot_rating': 3, 'character_rating': 4, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user2'}]}
        assert (books.get_about_data(3, 1) == exp)

        exp = {'title': 'Book 4', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'purchase_link': '', 'release_date': '02/02/2022', 'isbn': '0444444444', 'author': 'Author 2', 'author_about': "<p>This is the second author's about.</p>", 'author_number_followers': 3, 'num_want_read': 0, 'num_reading': 0, 'num_read': 4, 'genres': ['Genre 2', 'Genre 1', 'Genre 5', 'Genre 10', 'Genre 3', 'Genre 9', 'Genre 6', 'Genre 7'], 'author_id': 2, 'average_rating': 2.75, 'num_ratings': 4, 'num_5_stars': 0, 'num_4_stars': 1, 'num_3_stars': 2, 'num_2_stars': 0, 'num_1_star': 1, 'current_user_review': {'review_id': 9, 'overall_rating': 3, 'plot_rating': 2, 'character_rating': 5, 'summary': None, 'rating_body': None}, 'author_following': True, 'reviews': [{'id': 12, 'overall_rating': 4, 'plot_rating': 3, 'character_rating': 5, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user4'}, {'id': 11, 'overall_rating': 1, 'plot_rating': 2, 'character_rating': 3, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user3'}, {'id': 10, 'overall_rating': 3, 'plot_rating': 3, 'character_rating': 4, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user2'}]}
        assert (books.get_about_data(4, 1) == exp)

        exp = {'title': 'Book 5', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'purchase_link': '', 'release_date': '02/02/2022', 'isbn': '0555555555', 'author': 'Author 1', 'author_about': "<p>This is the first author's about.</p>", 'author_number_followers': 2, 'num_want_read': 0, 'num_reading': 0, 'num_read': 1, 'genres': ['Genre 4', 'Genre 9', 'Genre 1', 'Genre 2', 'Genre 6', 'Genre 5', 'Genre 3', 'Genre 10'], 'author_id': 1, 'average_rating': 1.0, 'num_ratings': 1, 'num_5_stars': 0, 'num_4_stars': 0, 'num_3_stars': 0, 'num_2_stars': 0, 'num_1_star': 1, 'current_user_review': {'review_id': 13, 'overall_rating': 1, 'plot_rating': 2, 'character_rating': 1, 'summary': None, 'rating_body': None}, 'author_following': True, 'reviews': []}
        assert (books.get_about_data(5, 1) == exp)
    
    def test_get_about_data_no_user(self):
        exp = {'title': 'Book 1', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'purchase_link': '', 'release_date': '02/02/2022', 'isbn': '0111111111', 'author': 'Author 1', 'author_about': "<p>This is the first author's about.</p>", 'author_number_followers': 2, 'num_want_read': 0, 'num_reading': 0, 'num_read': 2, 'genres': ['Genre 8', 'Genre 9', 'Genre 4', 'Genre 7', 'Genre 5', 'Genre 2', 'Genre 1', 'Genre 10'], 'author_id': 1, 'average_rating': 3.5, 'num_ratings': 2, 'num_5_stars': 1, 'num_4_stars': 0, 'num_3_stars': 0, 'num_2_stars': 1, 'num_1_star': 0, 'current_user_review': None, 'author_following': False, 'reviews': [{'id': 2, 'overall_rating': 2, 'plot_rating': 3, 'character_rating': 1, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user3'}, {'id': 1, 'overall_rating': 5, 'plot_rating': 5, 'character_rating': 5, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user1'}]}
        assert (books.get_about_data(1, None) == exp)

        exp = {'title': 'Book 2', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'purchase_link': '', 'release_date': '02/02/2022', 'isbn': '0222222222', 'author': 'Author 2', 'author_about': "<p>This is the second author's about.</p>", 'author_number_followers': 3, 'num_want_read': 0, 'num_reading': 0, 'num_read': 3, 'genres': ['Genre 2', 'Genre 3', 'Genre 8', 'Genre 10', 'Genre 5', 'Genre 4', 'Genre 6', 'Genre 7'], 'author_id': 2, 'average_rating': 4.0, 'num_ratings': 3, 'num_5_stars': 1, 'num_4_stars': 1, 'num_3_stars': 1, 'num_2_stars': 0, 'num_1_star': 0, 'current_user_review': None, 'author_following': False, 'reviews': [{'id': 5, 'overall_rating': 4, 'plot_rating': 3, 'character_rating': 4, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user4'}, {'id': 4, 'overall_rating': 5, 'plot_rating': 2, 'character_rating': 5, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user2'}, {'id': 3, 'overall_rating': 3, 'plot_rating': 2, 'character_rating': 3, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user1'}]}
        assert (books.get_about_data(2, None) == exp)

        exp = {'title': 'Book 3', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'purchase_link': '', 'release_date': '02/02/2022', 'isbn': '0333333333', 'author': 'Author 3', 'author_about': "<p>This is the third author's about.</p>", 'author_number_followers': 0, 'num_want_read': 0, 'num_reading': 0, 'num_read': 3, 'genres': ['Genre 4', 'Genre 3', 'Genre 2', 'Genre 6', 'Genre 10', 'Genre 9', 'Genre 8', 'Genre 5'], 'author_id': 3, 'average_rating': 3.0, 'num_ratings': 3, 'num_5_stars': 1, 'num_4_stars': 0, 'num_3_stars': 1, 'num_2_stars': 0, 'num_1_star': 1, 'current_user_review': None, 'author_following': False, 'reviews': [{'id': 8, 'overall_rating': 3, 'plot_rating': 2, 'character_rating': 4, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user4'}, {'id': 7, 'overall_rating': 1, 'plot_rating': 1, 'character_rating': 2, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user3'}, {'id': 6, 'overall_rating': 5, 'plot_rating': 3, 'character_rating': 4, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user2'}]}
        assert (books.get_about_data(3, None) == exp)

        exp = {'title': 'Book 4', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'purchase_link': '', 'release_date': '02/02/2022', 'isbn': '0444444444', 'author': 'Author 2', 'author_about': "<p>This is the second author's about.</p>", 'author_number_followers': 3, 'num_want_read': 0, 'num_reading': 0, 'num_read': 4, 'genres': ['Genre 2', 'Genre 1', 'Genre 5', 'Genre 10', 'Genre 3', 'Genre 9', 'Genre 6', 'Genre 7'], 'author_id': 2, 'average_rating': 2.75, 'num_ratings': 4, 'num_5_stars': 0, 'num_4_stars': 1, 'num_3_stars': 2, 'num_2_stars': 0, 'num_1_star': 1, 'current_user_review': None, 'author_following': False, 'reviews': [{'id': 12, 'overall_rating': 4, 'plot_rating': 3, 'character_rating': 5, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user4'}, {'id': 11, 'overall_rating': 1, 'plot_rating': 2, 'character_rating': 3, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user3'}, {'id': 10, 'overall_rating': 3, 'plot_rating': 3, 'character_rating': 4, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user2'}, {'id': 9, 'overall_rating': 3, 'plot_rating': 2, 'character_rating': 5, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user1'}]}
        assert (books.get_about_data(4, None) == exp)

        exp = {'title': 'Book 5', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'purchase_link': '', 'release_date': '02/02/2022', 'isbn': '0555555555', 'author': 'Author 1', 'author_about': "<p>This is the first author's about.</p>", 'author_number_followers': 2, 'num_want_read': 0, 'num_reading': 0, 'num_read': 1, 'genres': ['Genre 4', 'Genre 9', 'Genre 1', 'Genre 2', 'Genre 6', 'Genre 5', 'Genre 3', 'Genre 10'], 'author_id': 1, 'average_rating': 1.0, 'num_ratings': 1, 'num_5_stars': 0, 'num_4_stars': 0, 'num_3_stars': 0, 'num_2_stars': 0, 'num_1_star': 1, 'current_user_review': None, 'author_following': False, 'reviews': [{'id': 13, 'overall_rating': 1, 'plot_rating': 2, 'character_rating': 1, 'summary': None, 'rating_body': None, 'date_added': '12/02/2024', 'username': 'user1'}]}
        assert (books.get_about_data(5, None) == exp)

    def test_get_about_data_unknown(self):
        self.assertRaises(
            components.books.BookNotFoundError,
            books.get_about_data,
            500,
            None
        )

    def test_get_highest_rated(self):
        exp = {0: {'author': 'Author 2', 'title': 'Book 2', 'book_id': 2, 'cover': ''}, 1: {'author': 'Author 1', 'title': 'Book 1', 'book_id': 1, 'cover': ''}, 2: {'author': 'Author 3', 'title': 'Book 3', 'book_id': 3, 'cover': ''}, 3: {'author': 'Author 2', 'title': 'Book 4', 'book_id': 4, 'cover': ''}, 4: {'author': 'Author 1', 'title': 'Book 5', 'book_id': 5, 'cover': ''}}
        assert (books.get_highly_rated() == exp)


if __name__ == "__main__":
    test_leave_review()
    test_leave_review_existing()
    test_remove_review_valid()
    test_remove_review_invalid_bad_review()
    test_remove_review_invalid_bad_user()

    input("Press any key to proceed")

    unittest.main()