# -----------------------------------------------------------------------------
# Standard Python library imports
# -----------------------------------------------------------------------------
import math
import random
import datetime
import numpy as np
import sklearn.metrics

# -----------------------------------------------------------------------------
# Project imports
# -----------------------------------------------------------------------------
import os
import sys
import components.authors

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import configuration
import mysql_handler

# -----------------------------------------------------------------------------
# Project imports
# -----------------------------------------------------------------------------
class NoUserPreferencesError(Exception):
    def __init__(self, user_id):
        message = f"User with id {user_id}, has no preferences"
        super().__init__(message)

# -----------------------------------------------------------------------------
# Recommendations
# -----------------------------------------------------------------------------
class Recommendations:
    def __init__(self, connection, num_converge_iters, hyperparam, number_display_genres, initial_recommendation_mat_val, reading_list_percentage_increase, following_percentage_increase, bad_recommendation_value, minimum_required_reviews, number_recommendations, debug=False):
        self._connection = connection
        self._num_converge_iters = num_converge_iters
        self._hyperparam = hyperparam
        self._num_factors = len(self._connection.query("SELECT * FROM genres"))
        self.debug = debug
        self._num_users = len(self._connection.query("SELECT user_id FROM users"))
        self._num_books = len(self._connection.query("SELECT book_id FROM books"))
        self._number_recommendations = number_recommendations
        self._min_required_reviews = minimum_required_reviews
        self._initial_recommendation_mat_val = initial_recommendation_mat_val
        self._reading_list_percentage_increase = reading_list_percentage_increase
        self._following_percentage_increase = following_percentage_increase
        self._bad_recommendation_val = bad_recommendation_value  # This is not 0 as the genres may still be applicable, but should still be small
        self._num_display_genres = number_display_genres
        self.test_mse_record = []
        self.train_mse_record = []
        self._list_users_no_preferences = {i[0] for i in self._connection.query(
            "SELECT user_id FROM users WHERE preferences_set=FALSE")}
        # Uses a set as it is faster for 'item in var' operations

        # levels of configuration is required as the recommendations need to vary
        # depending on the hardware, and user base, such as average number of reviews,
        # sparsity of data, and preferences for recommendations, which would affect
        # how easily recommendations can change.

        self.gen_lookup_tables()
        self._load_book_factors()

    def _load_book_factors(self):
        self.book_factors = np.zeros((self._num_books, self._num_factors))

        res = self._connection.query("""
            SELECT book_id,
                GROUP_CONCAT(match_strength ORDER BY genre_id),
                GROUP_CONCAT(genre_id ORDER BY genre_id)
            FROM book_genres
            GROUP BY book_id
        """)

        for i, j, k in res:
            book_id = list(self.book_lookup_table.keys())[list(self.book_lookup_table.values()).index(i)]
            match_strengths = [float(z) for z in j.split(",")]
            genre_ids = [list(self.genre_lookup_table.keys())[list(self.genre_lookup_table.values()).index(int(z))] for z in k.split(",")]

            for genre, match in zip(genre_ids, match_strengths):
                self.book_factors[book_id][genre] = match

    def fit(self):
        train, test, = self.create_train_test()

        self._num_users, self._num_books = train.shape

        self.book_factors = np.random.random((self._num_books, self._num_factors))
        self.user_factors = np.random.random((self._num_users, self._num_factors))

        if self.debug:  # Debug is about 10 times slower
            self.test_mse_record = []
            self.train_mse_record = []

            for i in range(self._num_converge_iters):
                print(f"Iteration {i + 1} of {self._num_converge_iters} Start")
                self.user_factors = self.wals_step(train, self.book_factors)
                self.book_factors = self.wals_step(train.T, self.user_factors)

                predict = self.predict()

                self.train_mse_record.append(self.mean_squared_error(train, predict))
                self.test_mse_record.append(self.mean_squared_error(test, predict))
                print(f"Iteration {i + 1} of {self._num_converge_iters} End")

            return self.test_mse_record, self.train_mse_record

        else:
            for i in range(self._num_converge_iters):
                self.user_factors = self.wals_step(train, self.book_factors)
                self.book_factors = self.wals_step(train.T, self.user_factors)

            self.save_book_genres()  # Not included in the debug option, as it increases time cost,
            # and would likely be rerun a lot to find optimum parameters, so is unnecessary.

    def save_book_genres(self):
        query = "INSERT INTO book_genres (book_id, genre_id, match_strength) VALUES "
        for count, facts in enumerate(self.book_factors):
            # i will be the rating for each the genres.
            book_id = self.book_lookup_table[count]
            temp = ",".join(f"({book_id}, {self.genre_lookup_table[i]}, {strength})" for i, strength in enumerate(facts) if strength > 0)
            if len(temp):
                query += temp + ","

        self._connection.query("DELETE FROM book_genres")  # Done here to minimise time without data in DB
        self._connection.query(query[:-1])

    def predict(self):
        return self.user_factors.dot(self.book_factors.T)

    def gen_review_matrix(self):
        # x = np.array([[0.0 for i in range(num_books)] for k in range(num_users)])
        mat = np.zeros((self._num_users, self._num_books))
        for user in self.user_lookup_table:
            user_id = self.user_lookup_table[user]
            #    Reviews    #
            reviews = self._connection.query("""
                SELECT book_id,
                    (overall_rating + IFNULL(character_rating, overall_rating) + IFNULL(plot_rating, overall_rating)) / 3
                FROM reviews
                WHERE user_id={}
                GROUP BY review_id;
            """.format(user_id))

            for book_id, rating in reviews:
                used_book_id = list(self.book_lookup_table.values()).index(book_id)  # This finds the key for the value stored in the lookup table.
                # geeksforgeeks.org/python-get-key-from-value-in-dictionary
                mat[user][used_book_id] = float(rating)

            #    Initial Preferences    #
            books = self._connection.query("""
                SELECT books.book_id
                FROM initial_preferences
                INNER JOIN books
                    ON books.author_id=initial_preferences.author_id
                WHERE initial_preferences.user_id={}
                GROUP BY books.book_id
            """.format(user_id))  # Get a user's existing preferences

            if len(reviews) <= self._min_required_reviews:
                if len(books):
                    for i in books:
                        used_book_id = list(self.book_lookup_table.values()).index(i[0])
                        mat[user][used_book_id] += self._initial_recommendation_mat_val  # This is a non-zero value so recommendation is made.
                        # This is not affected by the average preference expressed by all the user's selected authors.
                else:
                    continue # The user has not set up any initial preferences yet.
            elif len(books):
                self._connection.query("""
                    DELETE FROM initial_preferences
                    WHERE user_id={}
                """.format(user_id))

            #    Reading Lists    #
            lists = self._connection.query("""
                SELECT reading_lists.book_id
                FROM reading_lists
                INNER JOIN reading_list_names
                    ON reading_lists.list_id=reading_list_names.list_id
                WHERE reading_lists.user_id={}
                GROUP BY reading_lists.book_id;
            """.format(user_id))

            for i in lists:
                used_book_id = list(self.book_lookup_table.values()).index(i[0])
                if mat[user][used_book_id] == 0:
                    mat[user][used_book_id] = self._initial_recommendation_mat_val
                else:
                    mat[user][used_book_id] *= (1 + self._reading_list_percentage_increase)

            #    Authors following    #
            following = self._connection.query("""
                SELECT books.book_id
                FROM author_followers
                INNER JOIN books
                    ON books.author_id=author_followers.author_id
                WHERE user_id={}
            """.format(user_id))

            for i in following:
                used_book_id = list(self.book_lookup_table.values()).index(int(i[0]))
                if mat[user][used_book_id] == 0:
                    mat[user][used_book_id] = self._initial_recommendation_mat_val
                else:
                    mat[user][used_book_id] *= (1 + self._following_percentage_increase)

            #    Bad Recommendations    #
            for book in self.get_bad_recommendations(user_id):
                used_book_id = list(self.book_lookup_table.values()).index(book)
                mat[user][used_book_id] = self._bad_recommendation_val  # = is used in case there is a good value here. It should be marked as bad.

            #    Diary entries    #
            entries = self._connection.query("""
                SELECT book_id,
                    (SUM(overall_rating) + SUM(IFNULL(character_rating, overall_rating)) + SUM(IFNULL(plot_rating, overall_rating))) / (COUNT(entry_id) * 3)
                FROM diary_entries
                WHERE user_id={}
                GROUP BY book_id;
            """.format(user_id))

            for book_id, rating in entries:
                used_book_id = list(self.book_lookup_table.values()).index(book_id)
                mat[user][used_book_id] += float(rating)  # += is used incase there is already a value at that index

        return mat

    def create_train_test(self, ratings=None):
        if ratings is None:
            self.ratings = self.gen_review_matrix()
        else:
            self.ratings = ratings

        train = self.ratings.copy()

        while self.ratings.tolist() == train.tolist():
            train = self.ratings.copy()
            for user in range(self._num_users):
                nonzero = self.ratings[user].nonzero()[0]
                indexes = np.random.choice(
                    nonzero,
                    size=round(len(nonzero) * 0.2),
                    replace=True
                )

                for i in indexes:
                    train[user, i] = 0.0

        return train, self.ratings

    def wals_step(self, ratings, fixed):
        A = fixed.T.dot(fixed) + np.eye(self._num_factors) * self._hyperparam
        B = ratings.dot(fixed)
        A_inv = np.linalg.inv(A)
        return B.dot(A_inv)

    def gen_lookup_tables(self):
        self.user_lookup_table = dict()
        users = self._connection.query("SELECT user_id FROM users")
        for count, i in enumerate(users):
            self.user_lookup_table[count] = i[0]

        self.book_lookup_table = dict()
        books = self._connection.query("SELECT book_id FROM books")
        for count, i in enumerate(books):
            self.book_lookup_table[count] = i[0]

        self.genre_lookup_table = dict()
        genres = self._connection.query("SELECT genre_id FROM genres")
        for count, i in enumerate(genres):
            self.genre_lookup_table[count] = i[0]

    def gen_recommendations(self):
        predictions = self.predict()

        query = "INSERT INTO recommendations (user_id, book_id, certainty) VALUES "

        self._list_users_no_preferences = {i[0] for i in self._connection.query(
            "SELECT user_id FROM users WHERE preferences_set=FALSE")}

        for user, books in enumerate(predictions):
            user_books = []
            user_id = self.user_lookup_table[user]

            if user_id not in self._list_users_no_preferences:
                avoid_recs = {
                    i[0] for i in self._connection.query("""
                        SELECT book_id
                        FROM recommendations
                        WHERE user_id={}
                            AND date_added>=DATE_SUB(NOW(), INTERVAL 2 DAY)
                    """.format(user_id))
                }  # sets are faster for "is val in list" operations

                res = self._connection.query("""
                    SELECT book_id
                    FROM reading_lists
                    INNER JOIN reading_list_names
                        ON reading_lists.list_id=reading_list_names.list_id
                    WHERE reading_lists.user_id={}
                        AND reading_list_names.list_name IN (
                            "Currently Reading",
                            "Have Read",
                            "Want To Read"
                        )
                """.format(user_id))  # Note that this covers the diary entries as well, as entries cannot be made unless it is in the have read/currently reading list

                for i in res:
                    avoid_recs.add(i[0])

                for i in self.get_bad_recommendations(user_id):
                    avoid_recs.add(i)

                for book, rating in enumerate(books):
                    book_id = self.book_lookup_table[book]
                    if book_id not in avoid_recs:
                        user_books.append({
                            "id": book_id,
                            "dot_product": rating
                        })

                user_books.sort(key=lambda x: x["dot_product"], reverse=True)
                user_books = user_books[:self._number_recommendations]

                for count, i in enumerate(user_books):  # Done after as this is faily expensive, to avoid unecessary calculations
                    user_books[count]["certainty"] = self.calculate_certainty(
                        i["id"],
                        user_id,
                        i["dot_product"]
                    )

                if len(user_books):
                    query += ",".join(
                        f"({user_id}, {i['id']}, {i['certainty']})" for i in user_books[:self._number_recommendations]) + ","

        self._connection.query("""
            DELETE FROM recommendations
            WHERE date_added<=DATE_SUB(NOW(), INTERVAL 2 DAY)
        """)

        self._connection.query(query[:-1])

    def delete_recommendation(self, user_id, book_id, bad_recommendation=True):
        # This includes marking a recommendation as bad - it is implicitly the same thing
        self._connection.query("""
            DELETE FROM recommendations
            WHERE user_id={user_id}
                AND book_id={book_id}
        """.format(
            user_id=user_id,
            book_id=book_id
        ))

        if bad_recommendation:
            self._connection.query(
                "INSERT INTO bad_recommendations (user_id, book_id) VALUES ({user_id}, {book_id})".format(
                    user_id=user_id,
                    book_id=book_id
                )
            )

    def get_bad_recommendations(self, user_id):
        bad_recommendations = self._connection.query("""
            SELECT recommendation_id,
                book_id,
                date_added
            FROM bad_recommendations
            WHERE user_id={}
        """.format(user_id))

        reading_list_items = self._connection.query("""
            SELECT reading_lists.book_id
            FROM reading_lists
            WHERE reading_lists.user_id={}
        """.format(user_id))

        return_vals = []
        remove = []
        for rec_id, book, date in bad_recommendations:
            if date + datetime.timedelta(weeks=10) > datetime.datetime.now():
                # 10 week expiry, so it can start recommending books if the user's preferences have changed. 10 weeks is
                # a long enough time for it to be plausible to be a good recommendation
                return_vals.append(book)
            else:
                remove.append(rec_id)

        if len(remove):
            self._connection.query(
                "DELETE FROM bad_recommendations WHERE recommendation_id IN ({})".format(",".join(str(i) for i in remove))
            )
            # Delete expired recommendations.

        return return_vals

    def get_user_recommendations(self, user_id):
        items = self._connection.query("""
            SELECT recommendations.book_id,
                ROUND(recommendations.certainty * 100, 1) as certainty,
                recommendations.date_added,
                books.cover_image,
                books.synopsis,
                books.title,
                authors.first_name,
                authors.surname,
                authors.alias,
                authors.author_id,
                (SELECT GROUP_CONCAT(genres.name ORDER BY book_genres.match_strength DESC LIMIT {genre_limit}) FROM book_genres
                    INNER JOIN genres ON book_genres.genre_id=genres.genre_id
                    WHERE book_genres.book_id=recommendations.book_id
                    GROUP BY books.book_id) AS genres,
                (SELECT ROUND(CAST(IFNULL(AVG(reviews.overall_rating), 0) as FLOAT), 2)
                    FROM reviews
                    WHERE reviews.book_id=books.book_id) AS average_rating,
                (SELECT COUNT(reviews.overall_rating)
                    FROM reviews
                    WHERE reviews.book_id=books.book_id) AS num_ratings
            FROM recommendations
            INNER JOIN books ON recommendations.book_id=books.book_id
            INNER JOIN authors ON books.author_id=authors.author_id
            WHERE recommendations.user_id={user_id}
            ORDER BY recommendations.certainty DESC;
        """.format(
            user_id=user_id,
            genre_limit=self._num_display_genres
        ))  # ORDER BY does not use calculated certainty for higher accuracy, and avoiding collisions
        # IFNULL prevents any null values - replace with 0s.

        self._list_users_no_preferences = {i[0] for i in self._connection.query(
            "SELECT user_id FROM users WHERE preferences_set=FALSE")}

        if len(items) == 0 or user_id in self._list_users_no_preferences:
            raise NoUserPreferencesError(user_id)

        output_dict = dict()
        for i, k in enumerate(items):
            author = components.authors.names_to_display(k[6], k[7], k[8])

            output_dict[i] = {
                "book_id": k[0],
                "certainty": k[1],
                "date_added": k[2].strftime("%d/%m/%Y"),
                "cover_image": k[3],
                "synopsis": "</p><p>".join(("<p>" + k[4] + "</p>").split("\n")),
                "title": k[5],
                "author_name": author,
                "author_id": k[9],
                "genres": k[10].split(","),
                "average_rating": round(k[11], 2),
                "number_ratings": k[12]
            }

        return output_dict

    def get_user_recommendation_summaries(self, user_id):
        res = self._connection.query("""
            SELECT books.book_id,
                books.title,
                books.cover_image,
                authors.first_name,
                authors.surname,
                authors.alias
            FROM recommendations
            INNER JOIN books ON recommendations.book_id=books.book_id
            INNER JOIN authors ON books.author_id=authors.author_id
            WHERE recommendations.user_id={}
            ORDER BY recommendations.certainty DESC;
        """.format(user_id))
        return [{
                "author": components.authors.names_to_display(i[3], i[4], i[5]),
                "title": i[1],
                "book_id": i[0],
                "cover": i[2],
            } for i in res]

    def calculate_certainty(self, book_id, user_id, dot_product, user_vec=None):
        if user_vec is None:
            user_id = list(self.user_lookup_table.values()).index(user_id)
            user_vec = [i for i in self.user_factors[user_id]]

        book_id = list(self.book_lookup_table.values()).index(book_id)
        book_vec = [i for i in self.book_factors[book_id]]

        abs_book_vec = math.sqrt(sum(i ** 2 for i in book_vec))
        abs_user_vec = math.sqrt(sum(i ** 2 for i in user_vec))

        try:
            similarity = dot_product / (abs_book_vec * abs_user_vec)
            if similarity > 1:  # Slim chance it ends up larger than 100%, so limits it artificially.
                similarity = 1
        except ZeroDivisionError:
            similarity = 0

        return similarity

    def add_user(self, user_id, author_ids):
        vals = [f"({user_id}, {author_id})" for author_id in author_ids]
        available_authors = {i[0] for i in self._connection.query("SELECT author_id FROM authors")}
        users = {i[0] for i in self._connection.query("SELECT user_id FROM users")}

        if set(author_ids).issubset(available_authors) and user_id in users:
            self._connection.query(
                "INSERT INTO initial_preferences (user_id, author_id) VALUES {}".format(
                    ",".join(vals)
                )
            )

            self._connection.query("""
                UPDATE users
                SET preferences_set=TRUE
                WHERE user_id={}
            """.format(user_id))

            res = self._connection.query("""
                    SELECT AVG(book_genres.match_strength),
                        book_genres.genre_id
                    FROM book_genres
                    INNER JOIN books
                        ON book_genres.book_id=books.book_id
                    INNER JOIN authors
                        ON books.author_id=authors.author_id
                    WHERE authors.author_id IN ({})
                    GROUP BY book_genres.genre_id;
                """.format(
                    ",".join(str(i) for i in author_ids)
                )
            )

            target_vec = np.zeros(self._num_factors)

            for avg, genre_id in res:
                genre = list(self.genre_lookup_table.values()).index(genre_id)
                target_vec[genre] = avg

            rec = (target_vec * self.book_factors).T

            output = []
            for count, val in enumerate(rec[0]):
                output.append({
                    "book_id": self.book_lookup_table[count],
                    "strength": val
                })

            output.sort(key=lambda x: x["strength"], reverse=True)

            output = output[:self._number_recommendations]

            for count, i in enumerate(output):
                output[count]["certainty"] = self.calculate_certainty(
                    i["book_id"],
                    user_id,
                    float(i["strength"]), # Convert the numpy float to a normal float so it can be used
                    target_vec
                )

            self._connection.query("INSERT INTO recommendations (user_id, book_id, certainty) VALUES {}".format(",".join(f"({user_id}, {i['book_id']}, {i['certainty']})" for i in output)))

            return output

    @staticmethod
    def mean_squared_error(true, pred):
        mask = np.nonzero(true)
        mse = sklearn.metrics.mean_squared_error(true[mask], pred[mask])
        return mse


# -----------------------------------------------------------------------------
# Plotting functions
# -----------------------------------------------------------------------------
def plot_learning_curve(model):
    import matplotlib.pyplot as plt  # This is bad practice, but cannot be imported with lighttpd
    linewidth = 3
    plt.plot(model.test_mse_record, label='Test', linewidth=linewidth)
    plt.plot(model.train_mse_record, label='Train', linewidth=linewidth)
    plt.xlabel('iterations')
    plt.ylabel('MSE')
    plt.legend(loc='best')
    plt.show()
