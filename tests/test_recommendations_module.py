import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend/")

import components.recommendations

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

class RecommendationTests(unittest.TestCase):
    def test_bad_recommendations(self):
        assert (recommendations.get_bad_recommendations(1) == [3, 5])
        assert (recommendations.get_bad_recommendations(2) == [1])
        assert (recommendations.get_bad_recommendations(3) == [])

    def test_bad_recommendations_unknown(self):
        assert (recommendations.get_bad_recommendations(400) == [])

    def test_get_recommendations(self):
        exp = {0: {'book_id': 1, 'certainty': 50.0, 'date_added': '15/02/2024', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'title': 'Book 1', 'author_name': 'Author 1', 'author_id': 1, 'genres': ['Genre 8', 'Genre 9', 'Genre 4', 'Genre 7', 'Genre 5', 'Genre 2', 'Genre 1', 'Genre 10'], 'average_rating': 3.5, 'number_ratings': 2}, 1: {'book_id': 2, 'certainty': 50.0, 'date_added': '15/02/2024', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'title': 'Book 2', 'author_name': 'Author 2', 'author_id': 2, 'genres': ['Genre 2', 'Genre 3', 'Genre 8', 'Genre 10', 'Genre 5', 'Genre 4', 'Genre 6', 'Genre 7'], 'average_rating': 4.0, 'number_ratings': 3}}
        assert (recommendations.get_user_recommendations(1) == exp)

        exp = {0: {'book_id': 4, 'certainty': 50.0, 'date_added': '15/02/2024', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'title': 'Book 4', 'author_name': 'Author 2', 'author_id': 2, 'genres': ['Genre 2', 'Genre 1', 'Genre 5', 'Genre 10', 'Genre 3', 'Genre 9', 'Genre 6', 'Genre 7'], 'average_rating': 2.75, 'number_ratings': 4}, 1: {'book_id': 3, 'certainty': 50.0, 'date_added': '15/02/2024', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'title': 'Book 3', 'author_name': 'Author 3', 'author_id': 3, 'genres': ['Genre 4', 'Genre 3', 'Genre 2', 'Genre 6', 'Genre 10', 'Genre 9', 'Genre 8', 'Genre 5'], 'average_rating': 3.0, 'number_ratings': 3}}
        assert (recommendations.get_user_recommendations(2) == exp)

        exp = {0: {'book_id': 5, 'certainty': 50.0, 'date_added': '15/02/2024', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'title': 'Book 5', 'author_name': 'Author 1', 'author_id': 1, 'genres': ['Genre 4', 'Genre 9', 'Genre 1', 'Genre 2', 'Genre 6', 'Genre 5', 'Genre 3', 'Genre 10'], 'average_rating': 1.0, 'number_ratings': 1}, 1: {'book_id': 1, 'certainty': 50.0, 'date_added': '15/02/2024', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'title': 'Book 1', 'author_name': 'Author 1', 'author_id': 1, 'genres': ['Genre 8', 'Genre 9', 'Genre 4', 'Genre 7', 'Genre 5', 'Genre 2', 'Genre 1', 'Genre 10'], 'average_rating': 3.5, 'number_ratings': 2}}
        assert (recommendations.get_user_recommendations(3) == exp)

        exp = {0: {'book_id': 2, 'certainty': 50.0, 'date_added': '15/02/2024', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'title': 'Book 2', 'author_name': 'Author 2', 'author_id': 2, 'genres': ['Genre 2', 'Genre 3', 'Genre 8', 'Genre 10', 'Genre 5', 'Genre 4', 'Genre 6', 'Genre 7'], 'average_rating': 4.0, 'number_ratings': 3}, 1: {'book_id': 3, 'certainty': 50.0, 'date_added': '15/02/2024', 'cover_image': '', 'synopsis': '<p>This book does not have a synopsis</p>', 'title': 'Book 3', 'author_name': 'Author 3', 'author_id': 3, 'genres': ['Genre 4', 'Genre 3', 'Genre 2', 'Genre 6', 'Genre 10', 'Genre 9', 'Genre 8', 'Genre 5'], 'average_rating': 3.0, 'number_ratings': 3}}
        assert (recommendations.get_user_recommendations(4) == exp)

    def test_get_recommendations_no_preference(self):
        self.assertRaises(
            components.recommendations.NoUserPreferencesError,
            recommendations.get_user_recommendations,
            5
        )

    def test_get_summaries(self):
        exp = [{'author': 'Author 1', 'title': 'Book 1', 'book_id': 1, 'cover': ''}, {'author': 'Author 2', 'title': 'Book 2', 'book_id': 2, 'cover': ''}]
        assert (recommendations.get_user_recommendation_summaries(1) == exp)

        exp = [{'author': 'Author 2', 'title': 'Book 4', 'book_id': 4, 'cover': ''}, {'author': 'Author 3', 'title': 'Book 3', 'book_id': 3, 'cover': ''}]
        assert (recommendations.get_user_recommendation_summaries(2) == exp)

        exp = [{'author': 'Author 1', 'title': 'Book 5', 'book_id': 5, 'cover': ''}, {'author': 'Author 1', 'title': 'Book 1', 'book_id': 1, 'cover': ''}]
        assert (recommendations.get_user_recommendation_summaries(3) == exp)

        exp = [{'author': 'Author 2', 'title': 'Book 2', 'book_id': 2, 'cover': ''}, {'author': 'Author 3', 'title': 'Book 3', 'book_id': 3, 'cover': ''}]
        assert (recommendations.get_user_recommendation_summaries(4) == exp)

        assert (recommendations.get_user_recommendation_summaries(5) == [])

    def test_get_summaries_unknown(self):
        assert (recommendations.get_user_recommendation_summaries(400) == [])

def fit():
    input("Press enter to proceed")
    print("Check addition of new genres")
    recommendations.fit()

def generate_recommendations():
    input("Press enter to proceed")
    print("Check addition of new recommendations")
    recommendations.gen_recommendations()

def delete_recommendation():
    input("Press enter to proceed")
    print("Check removal of recommendations and no change to bad recommendations")
    recommendations.delete_recommendation(1,1, bad_recommendation=False)

    input("Press enter to proceed")
    print("Check removal of recommendations and addition to bad recommendations")
    recommendations.delete_recommendation(1, 1, bad_recommendation=True)

def add_user():
    input("Press enter to proceed")
    print("Check additon of inital user preferences and recommendations")
    recommendations.add_user(5, [1, 3])

    input("Press enter to proceed")
    print("Check no change")
    recommendations.add_user(5, [1, 4])

    input("Press enter to proceed")
    print("Check no change")
    recommendations.add_user(500, [1, 2])

if __name__ == "__main__":
    fit()
    generate_recommendations()
    delete_recommendation()
    add_user()

    input("Press enter to proceed (add add-on data)")
    unittest.main()