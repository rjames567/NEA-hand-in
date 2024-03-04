import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend/")

import components.authors
import components.books
import components.genres
import components.information_retrieval
import components.reading_lists
import components.recommendations

import configuration
import environ_manipulation
import logger
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

number_home_summaries = config.get("home number_home_summaries")

genres = components.genres.Genres(connection)
authors = components.authors.Authors(
    connection,
    config.get("number_display_genres"),
    number_home_summaries
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
books = components.books.Books(
    connection,
    reading_lists,
    config.get("home number_about_similarities"),
    number_home_summaries,
    config.get("number_display_genres")
)
information_retrieval = components.information_retrieval.DocumentCollection(
    connection,
    books,
    authors,
    genres,
    config.get("search number_results")
)

class SearchingTest(unittest.TestCase):
    def test_isbn_valid(self):
        exp = {0: {'author': 'Author 1', 'title': 'Book 1', 'book_id': 1, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("0111111111") == exp)

        exp = {0: {'author': 'Author 2', 'title': 'Book 2', 'book_id': 2, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("0222222222") == exp)

        exp = {0: {'author': 'Author 3', 'title': 'Book 3', 'book_id': 3, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("0333333333") == exp)

        exp = {0: {'author': 'Author 2', 'title': 'Book 4', 'book_id': 4, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("0444444444") == exp)

        exp = {0: {'author': 'Author 1', 'title': 'Book 5', 'book_id': 5, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("0555555555") == exp)

        exp = {0: {'author': 'Kristin Hannah', 'title': 'The Nightingale', 'book_id': 6, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("41125521") == exp)

        exp = {0: {'author': 'Author 3', 'title': 'Animal Farm', 'book_id': 7, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("2207778") == exp)

        exp = {0: {'author': 'Mary E. Pearson', 'title': 'The Kiss of Deception (The Remnant Chronicles, #1)', 'book_id': 8, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("22617247") == exp)

        exp = {0: {'author': 'Rick Riordan', 'title': 'The Sea of Monsters (Percy Jackson and the Olympians, #2)', 'book_id': 9, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("43554") == exp)

        exp = {0: {'author': 'Rick Riordan', 'title': 'The Son of Neptune (The Heroes of Olympus, #2)', 'book_id': 10, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("14406312") == exp)

        exp = {0: {'author': 'Rick Riordan', 'title': 'The Last Olympian (Percy Jackson and the Olympians, #5)', 'book_id': 11, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("4551489") == exp)

        exp = {0: {'author': 'Rick Riordan', 'title': 'The Sword of Summer (Magnus Chase and the Gods of Asgard, #1)', 'book_id': 12, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("21400019") == exp)

        exp = {0: {'author': 'Rick Riordan', 'title': 'The Red Pyramid (Kane Chronicles, #1)', 'book_id': 13, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("346572") == exp)

        exp = {0: {'author': 'Alyson Noel', 'title': 'Evermore (The Immortals, #1)', 'book_id': 14, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("4021549") == exp)

        exp = {0: {'author': 'Marie Kondo', 'title': 'The Life-Changing Magic of Tidying Up: The Japanese Art of Decluttering and Organizing', 'book_id': 15, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("41711738") == exp)

        exp = {0: {'author': 'Barbara Kingsolver', 'title': 'The Poisonwood Bible', 'book_id': 16, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("810663") == exp)

        exp = {0: {'author': 'Susan Ee', 'title': 'Angelfall (Penryn & the End of Days, #1)', 'book_id': 17, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("16435765") == exp)

        exp = {0: {'author': 'Bill Bryson', 'title': 'A Walk in the Woods', 'book_id': 18, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("613469") == exp)

        exp = {0: {'author': 'Jennifer L. Armentrout', 'title': 'Onyx (Lux, #2)', 'book_id': 19, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("18211575") == exp)

        exp = {0: {'author': 'Jennifer L. Armentrout', 'title': 'Opal (Lux, #3)', 'book_id': 20, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("18591132") == exp)

        exp = {0: {'author': 'Jennifer L. Armentrout', 'title': 'Origin (Lux, #4)', 'book_id': 21, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("19259997") == exp)

        exp = {0: {'author': 'Kristin Cashore', 'title': 'Graceling (Graceling Realm, #1)', 'book_id': 22, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("3270810") == exp)

        exp = {0: {'author': 'Aziz Ansari', 'title': 'Modern Romance', 'book_id': 23, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("43014915") == exp)

    def test_isbn_unknown(self):
        assert (information_retrieval.database_search("1234567890") == dict())
    
    def test_author_known(self):
        exp = {0: {'name': 'Kristin Hannah', 'type': 'a', 'author_id': 4, 'certainty': 100.0}, 1: {'author': 'Kristin Hannah', 'title': 'The Nightingale', 'book_id': 6, 'cover': '', 'type': 'b', 'certainty': 100.0}, 2: {'name': 'Kristin Cashore', 'type': 'a', 'author_id': 20, 'certainty': 62.0}, 3: {'author': 'Kristin Cashore', 'title': 'Graceling (Graceling Realm, #1)', 'book_id': 22, 'cover': '', 'type': 'b', 'certainty': 62.0}}
        assert (information_retrieval.database_search("Kristin Hannah") == exp)

        exp = {0: {'name': 'Kurt Vonnegut Jr.', 'type': 'a', 'author_id': 8, 'certainty': 100.0}}
        assert (information_retrieval.database_search("Kurt") == exp)

        exp = {0: {'name': "Madeleine L'Engle", 'type': 'a', 'author_id': 10, 'certainty': 100.0}}
        assert (information_retrieval.database_search("l'engle") == exp)

        exp = {0: {'name': 'Jennifer L. Armentrout', 'type': 'a', 'author_id': 19, 'certainty': 100.0}, 1: {'author': 'Jennifer L. Armentrout', 'title': 'Onyx (Lux, #2)', 'book_id': 19, 'cover': '', 'type': 'b', 'certainty': 100.0}, 2: {'author': 'Jennifer L. Armentrout', 'title': 'Opal (Lux, #3)', 'book_id': 20, 'cover': '', 'type': 'b', 'certainty': 100.0}, 3: {'author': 'Jennifer L. Armentrout', 'title': 'Origin (Lux, #4)', 'book_id': 21, 'cover': '', 'type': 'b', 'certainty': 100.0}}
        assert (information_retrieval.database_search("Armentrout, Jennifer") == exp)

    def test_author_unknown(self):
        assert (information_retrieval.database_search("Bob") == dict())
        assert (information_retrieval.database_search("Arbitrary writer") == dict())

    def test_genre_known(self):
        exp = {0: {'name': 'Genre 1', 'type': 'g', 'certainty': 100.0}, 1: {'name': 'Genre 2', 'type': 'g', 'certainty': 72.7}, 2: {'name': 'Genre 3', 'type': 'g', 'certainty': 72.7}, 3: {'name': 'Genre 4', 'type': 'g', 'certainty': 72.7}, 4: {'name': 'Genre 5', 'type': 'g', 'certainty': 72.7}, 5: {'name': 'Genre 6', 'type': 'g', 'certainty': 72.7}, 6: {'name': 'Genre 7', 'type': 'g', 'certainty': 72.7}, 7: {'name': 'Genre 8', 'type': 'g', 'certainty': 72.7}, 8: {'name': 'Genre 9', 'type': 'g', 'certainty': 72.7}, 9: {'name': 'Genre 10', 'type': 'g', 'certainty': 72.7}, 10: {'author': 'Mary E. Pearson', 'title': 'The Kiss of Deception (The Remnant Chronicles, #1)', 'book_id': 8, 'cover': '', 'type': 'b', 'certainty': 68.6}, 11: {'name': 'Author 1', 'type': 'a', 'author_id': 1, 'certainty': 68.6}, 12: {'author': 'Author 1', 'title': 'Book 1', 'book_id': 1, 'cover': '', 'type': 'b', 'certainty': 68.6}, 13: {'author': 'Author 1', 'title': 'Book 5', 'book_id': 5, 'cover': '', 'type': 'b', 'certainty': 68.6}, 14: {'author': 'Rick Riordan', 'title': 'The Sword of Summer (Magnus Chase and the Gods of Asgard, #1)', 'book_id': 12, 'cover': '', 'type': 'b', 'certainty': 68.6}, 15: {'author': 'Rick Riordan', 'title': 'The Red Pyramid (Kane Chronicles, #1)', 'book_id': 13, 'cover': '', 'type': 'b', 'certainty': 68.6}, 16: {'author': 'Alyson Noel', 'title': 'Evermore (The Immortals, #1)', 'book_id': 14, 'cover': '', 'type': 'b', 'certainty': 68.6}, 17: {'author': 'Susan Ee', 'title': 'Angelfall (Penryn & the End of Days, #1)', 'book_id': 17, 'cover': '', 'type': 'b', 'certainty': 68.6}, 18: {'author': 'Kristin Cashore', 'title': 'Graceling (Graceling Realm, #1)', 'book_id': 22, 'cover': '', 'type': 'b', 'certainty': 68.6}}
        assert (information_retrieval.database_search("Genre 1") == exp)

        exp = {0: {'name': 'Genre 2', 'type': 'g', 'certainty': 100.0}, 1: {'author': 'Rick Riordan', 'title': 'The Sea of Monsters (Percy Jackson and the Olympians, #2)', 'book_id': 9, 'cover': '', 'type': 'b', 'certainty': 77.1}, 2: {'author': 'Jennifer L. Armentrout', 'title': 'Onyx (Lux, #2)', 'book_id': 19, 'cover': '', 'type': 'b', 'certainty': 77.1}, 3: {'name': 'Author 2', 'type': 'a', 'author_id': 2, 'certainty': 77.1}, 4: {'author': 'Author 2', 'title': 'Book 2', 'book_id': 2, 'cover': '', 'type': 'b', 'certainty': 77.1}, 5: {'author': 'Author 2', 'title': 'Book 4', 'book_id': 4, 'cover': '', 'type': 'b', 'certainty': 77.1}, 6: {'author': 'Rick Riordan', 'title': 'The Son of Neptune (The Heroes of Olympus, #2)', 'book_id': 10, 'cover': '', 'type': 'b', 'certainty': 77.1}, 7: {'name': 'Genre 1', 'type': 'g', 'certainty': 63.7}, 8: {'name': 'Genre 3', 'type': 'g', 'certainty': 63.7}, 9: {'name': 'Genre 4', 'type': 'g', 'certainty': 63.7}, 10: {'name': 'Genre 5', 'type': 'g', 'certainty': 63.7}, 11: {'name': 'Genre 6', 'type': 'g', 'certainty': 63.7}, 12: {'name': 'Genre 7', 'type': 'g', 'certainty': 63.7}, 13: {'name': 'Genre 8', 'type': 'g', 'certainty': 63.7}, 14: {'name': 'Genre 9', 'type': 'g', 'certainty': 63.7}, 15: {'name': 'Genre 10', 'type': 'g', 'certainty': 63.7}}
        assert (information_retrieval.database_search("Genre 2") == exp)

        exp = {0: {'name': 'Genre 3', 'type': 'g', 'certainty': 100.0}, 1: {'author': 'Jennifer L. Armentrout', 'title': 'Opal (Lux, #3)', 'book_id': 20, 'cover': '', 'type': 'b', 'certainty': 81.5}, 2: {'name': 'Author 3', 'type': 'a', 'author_id': 3, 'certainty': 81.5}, 3: {'author': 'Author 3', 'title': 'Book 3', 'book_id': 3, 'cover': '', 'type': 'b', 'certainty': 81.5}, 4: {'author': 'Author 3', 'title': 'Animal Farm', 'book_id': 7, 'cover': '', 'type': 'b', 'certainty': 81.5}, 5: {'name': 'Genre 1', 'type': 'g', 'certainty': 57.9}, 6: {'name': 'Genre 2', 'type': 'g', 'certainty': 57.9}, 7: {'name': 'Genre 4', 'type': 'g', 'certainty': 57.9}, 8: {'name': 'Genre 5', 'type': 'g', 'certainty': 57.9}, 9: {'name': 'Genre 6', 'type': 'g', 'certainty': 57.9}, 10: {'name': 'Genre 7', 'type': 'g', 'certainty': 57.9}, 11: {'name': 'Genre 8', 'type': 'g', 'certainty': 57.9}, 12: {'name': 'Genre 9', 'type': 'g', 'certainty': 57.9}, 13: {'name': 'Genre 10', 'type': 'g', 'certainty': 57.9}}
        assert (information_retrieval.database_search("Genre 3") == exp)

    def test_genre_unknown(self):
        assert (information_retrieval.database_search("Arbitrary Genre-name") == dict())

    def test_book_known(self):
        exp = {0: {'author': 'Author 3', 'title': 'Animal Farm', 'book_id': 7, 'cover': '', 'type': 'b', 'certainty': 92.8}, 1: {'author': 'Rick Riordan', 'title': 'The Sea of Monsters (Percy Jackson and the Olympians, #2)', 'book_id': 9, 'cover': '', 'type': 'b', 'certainty': 37.3}, 2: {'author': 'Alyson Noel', 'title': 'Evermore (The Immortals, #1)', 'book_id': 14, 'cover': '', 'type': 'b', 'certainty': 37.3}, 3: {'author': 'Mary E. Pearson', 'title': 'The Kiss of Deception (The Remnant Chronicles, #1)', 'book_id': 8, 'cover': '', 'type': 'b', 'certainty': 37.3}, 4: {'author': 'Rick Riordan', 'title': 'The Son of Neptune (The Heroes of Olympus, #2)', 'book_id': 10, 'cover': '', 'type': 'b', 'certainty': 37.3}, 5: {'author': 'Rick Riordan', 'title': 'The Last Olympian (Percy Jackson and the Olympians, #5)', 'book_id': 11, 'cover': '', 'type': 'b', 'certainty': 37.3}, 6: {'author': 'Rick Riordan', 'title': 'The Sword of Summer (Magnus Chase and the Gods of Asgard, #1)', 'book_id': 12, 'cover': '', 'type': 'b', 'certainty': 37.3}, 7: {'author': 'Marie Kondo', 'title': 'The Life-Changing Magic of Tidying Up: The Japanese Art of Decluttering and Organizing', 'book_id': 15, 'cover': '', 'type': 'b', 'certainty': 37.3}, 8: {'author': 'Susan Ee', 'title': 'Angelfall (Penryn & the End of Days, #1)', 'book_id': 17, 'cover': '', 'type': 'b', 'certainty': 37.3}, 9: {'author': 'Bill Bryson', 'title': 'A Walk in the Woods', 'book_id': 18, 'cover': '', 'type': 'b', 'certainty': 37.3}, 10: {'author': 'Kristin Hannah', 'title': 'The Nightingale', 'book_id': 6, 'cover': '', 'type': 'b', 'certainty': 37.3}, 11: {'author': 'Rick Riordan', 'title': 'The Red Pyramid (Kane Chronicles, #1)', 'book_id': 13, 'cover': '', 'type': 'b', 'certainty': 37.3}}
        assert (information_retrieval.database_search("The animal") == exp)

        exp = {0: {'author': 'Rick Riordan', 'title': 'The Sea of Monsters (Percy Jackson and the Olympians, #2)', 'book_id': 9, 'cover': '', 'type': 'b', 'certainty': 95.0}, 1: {'author': 'Rick Riordan', 'title': 'The Last Olympian (Percy Jackson and the Olympians, #5)', 'book_id': 11, 'cover': '', 'type': 'b', 'certainty': 95.0}, 2: {'author': 'Mary E. Pearson', 'title': 'The Kiss of Deception (The Remnant Chronicles, #1)', 'book_id': 8, 'cover': '', 'type': 'b', 'certainty': 43.7}, 3: {'author': 'Rick Riordan', 'title': 'The Son of Neptune (The Heroes of Olympus, #2)', 'book_id': 10, 'cover': '', 'type': 'b', 'certainty': 43.7}, 4: {'author': 'Alyson Noel', 'title': 'Evermore (The Immortals, #1)', 'book_id': 14, 'cover': '', 'type': 'b', 'certainty': 43.7}, 5: {'author': 'Kristin Hannah', 'title': 'The Nightingale', 'book_id': 6, 'cover': '', 'type': 'b', 'certainty': 43.7}, 6: {'author': 'Rick Riordan', 'title': 'The Sword of Summer (Magnus Chase and the Gods of Asgard, #1)', 'book_id': 12, 'cover': '', 'type': 'b', 'certainty': 43.7}, 7: {'author': 'Rick Riordan', 'title': 'The Red Pyramid (Kane Chronicles, #1)', 'book_id': 13, 'cover': '', 'type': 'b', 'certainty': 43.7}, 8: {'author': 'Marie Kondo', 'title': 'The Life-Changing Magic of Tidying Up: The Japanese Art of Decluttering and Organizing', 'book_id': 15, 'cover': '', 'type': 'b', 'certainty': 43.7}, 9: {'author': 'Susan Ee', 'title': 'Angelfall (Penryn & the End of Days, #1)', 'book_id': 17, 'cover': '', 'type': 'b', 'certainty': 43.7}, 10: {'author': 'Bill Bryson', 'title': 'A Walk in the Woods', 'book_id': 18, 'cover': '', 'type': 'b', 'certainty': 43.7}}
        assert (information_retrieval.database_search("The olympians") == exp)

        exp = {0: {'author': 'Rick Riordan', 'title': 'The Sword of Summer (Magnus Chase and the Gods of Asgard, #1)', 'book_id': 12, 'cover': '', 'type': 'b', 'certainty': 95.8}, 1: {'author': 'Marie Kondo', 'title': 'The Life-Changing Magic of Tidying Up: The Japanese Art of Decluttering and Organizing', 'book_id': 15, 'cover': '', 'type': 'b', 'certainty': 36.7}, 2: {'author': 'Susan Ee', 'title': 'Angelfall (Penryn & the End of Days, #1)', 'book_id': 17, 'cover': '', 'type': 'b', 'certainty': 36.7}, 3: {'author': 'Rick Riordan', 'title': 'The Son of Neptune (The Heroes of Olympus, #2)', 'book_id': 10, 'cover': '', 'type': 'b', 'certainty': 36.7}, 4: {'author': 'Rick Riordan', 'title': 'The Sea of Monsters (Percy Jackson and the Olympians, #2)', 'book_id': 9, 'cover': '', 'type': 'b', 'certainty': 34.6}, 5: {'author': 'Mary E. Pearson', 'title': 'The Kiss of Deception (The Remnant Chronicles, #1)', 'book_id': 8, 'cover': '', 'type': 'b', 'certainty': 34.6}, 6: {'author': 'Bill Bryson', 'title': 'A Walk in the Woods', 'book_id': 18, 'cover': '', 'type': 'b', 'certainty': 21.6}, 7: {'author': 'Kristin Hannah', 'title': 'The Nightingale', 'book_id': 6, 'cover': '', 'type': 'b', 'certainty': 21.6}, 8: {'author': 'Rick Riordan', 'title': 'The Last Olympian (Percy Jackson and the Olympians, #5)', 'book_id': 11, 'cover': '', 'type': 'b', 'certainty': 21.6}, 9: {'author': 'Rick Riordan', 'title': 'The Red Pyramid (Kane Chronicles, #1)', 'book_id': 13, 'cover': '', 'type': 'b', 'certainty': 21.6}, 10: {'author': 'Alyson Noel', 'title': 'Evermore (The Immortals, #1)', 'book_id': 14, 'cover': '', 'type': 'b', 'certainty': 21.6}}
        assert (information_retrieval.database_search("The sword of magnus chase") == exp)

    def test_book_unknown(self):
        assert (information_retrieval.database_search("An arbitrary book's title") == dict())

def test_unique_words():
    input("Press enter to proceed")
    connection.query("DELETE FROM unique_words")
    input("Press enter to proceed")
    print("Check addition of words")
    information_retrieval.gen_unique_words()

def test_idf_values():
    input("Press enter to proceed")
    connection.query("DELETE FROM unique_words")
    input("Press enter to proceed")
    print("Check addition of words")
    information_retrieval.gen_unique_words()
    information_retrieval.gen_idf_values()

if __name__ == "__main__":
    test_unique_words()
    test_idf_values()

    input("Press enter to proceed")

    unittest.main()