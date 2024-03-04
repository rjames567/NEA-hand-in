# -----------------------------------------------------------------------------
# Project imports
# -----------------------------------------------------------------------------
import components.authors

import sys
import mysql.connector
sys.path.append("../backend")

import data_structures

# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------
class ListNotFoundError(Exception):
    def __init__(self, list_name, user_id):
        message = f"User with id '{user_id} does not have a list called {list_name}."
        super().__init__(message)

# -----------------------------------------------------------------------------
# Objects
# -----------------------------------------------------------------------------
class ReadingLists:
    def __init__(self, connection, number_summaries_home, num_display_genres, recommendations):
        self._recommendations = recommendations
        self._connection = connection
        self._number_summaries_home = number_summaries_home
        self._num_display_genres = num_display_genres

    def get_popular(self):
        res = self._connection.query("""
            SELECT books.book_id,
                books.title,
                books.cover_image,
                authors.first_name,
                authors.surname,
                authors.alias,
                COUNT(books.book_id) as num
            FROM books
            INNER JOIN authors
                ON books.author_id=authors.author_id
            INNER JOIN reading_lists
                ON reading_lists.book_id=books.book_id
            INNER JOIN reading_list_names
                ON reading_list_names.list_id=reading_lists.list_id
            WHERE reading_list_names.list_name="Currently Reading"
            GROUP BY books.book_id
            ORDER BY num DESC
            LIMIT {};
        """.format(self._number_summaries_home))

        output_dict = dict()
        for i, k in enumerate(res):
            output_dict[i] = {
                "author": components.authors.names_to_display(k[3], k[4], k[5]),
                "title": k[1],
                "book_id": k[0],
                "cover": k[2],
            }
        
        return output_dict
    
    def get_list_id(self, list_name, user_id):
        res = self._connection.query("""
            SELECT list_id
            FROM reading_list_names
            WHERE user_id={user_id}
                AND list_name="{list_name}";
        """.format(user_id=user_id, list_name=list_name))

        if len(res) == 0:
            raise ListNotFoundError(list_name, user_id)
        
        return res[0][0]

    def get_names(self, user_id):
        res = self._connection.query(
            """
            SELECT list_id, list_name FROM reading_list_names
            WHERE user_id={};
            """.format(user_id)
        )  # List of single element tuples
        output_queue = data_structures.Queue()
        for i in res:
            output_queue.push({
                "id": i[0],
                "name": i[1]
            })

        return output_queue

    def get_currently_reading(self, user_id):
        res = self._connection.query("""
            SELECT books.book_id,
                books.title,
                books.cover_image,
                authors.first_name,
                authors.surname,
                authors.alias
            FROM reading_lists
            INNER JOIN books
                ON reading_lists.book_id=books.book_id
            INNER JOIN authors
                ON books.author_id=authors.author_id
            INNER JOIN reading_list_names
                ON reading_list_names.list_id=reading_lists.list_id
            WHERE reading_list_names.list_name="Currently Reading"
                AND reading_list_names.user_id={};
        """.format(user_id))
        return [{
                "author": components.authors.names_to_display(i[3], i[4], i[5]),
                "title": i[1],
                "book_id": i[0],
                "cover": i[2],
            } for i in res]

    def get_want_read(self, user_id):
        res = self._connection.query("""
            SELECT books.book_id,
                books.title,
                books.cover_image,
                authors.first_name,
                authors.surname,
                authors.alias
            FROM reading_lists
            INNER JOIN books
                ON reading_lists.book_id=books.book_id
            INNER JOIN authors
                ON books.author_id=authors.author_id
            INNER JOIN reading_list_names
                ON reading_list_names.list_id=reading_lists.list_id
            WHERE reading_list_names.list_name="Want to Read"
                AND reading_list_names.user_id={};
        """.format(user_id))
        return [{
                "author": components.authors.names_to_display(i[3], i[4], i[5]),
                "title": i[1],
                "book_id": i[0],
                "cover": i[2],
            } for i in res]

    def get_names_check_book_in(self, user_id, book_id):
        res = self._connection.query(
            """
            SELECT list_id, list_name FROM reading_list_names
            WHERE user_id={};
            """.format(user_id)
        )

        lists = dict()
        for i, k in enumerate(res):
            list_id, list_name = k
            in_list = bool(len(self._connection.query("""
                SELECT book_id FROM reading_lists
                WHERE list_id={list_id}
                    AND book_id={book_id};
            """.format(list_id=list_id, book_id=book_id))))
            lists[i] = {
                "id": list_id,
                "list_name": list_name,
                "has_book": in_list
            }

        return lists

    def get_values(self, list_id, user_id):
        res = self._connection.query("""
            SELECT books.book_id,
                books.cover_image,
                books.title,
                books.synopsis,
                authors.first_name,
                authors.surname,
                authors.alias,
                authors.author_id,
                reading_lists.date_added,
                (SELECT GROUP_CONCAT(genres.name)
                    FROM book_genres
                    inner join books on book_genres.book_id=books.book_id
                    inner join genres on genres.genre_id=book_genres.genre_id
                    WHERE book_genres.book_id=reading_lists.book_id
                    GROUP by books.title) AS genres,
                (SELECT CAST(IFNULL(AVG(reviews.overall_rating), 0) as FLOAT) 
                    FROM reviews
                    WHERE reviews.book_id=books.book_id) AS average_rating,
                (SELECT COUNT(reviews.overall_rating)
                    FROM reviews
                    WHERE reviews.book_id=books.book_id) AS num_ratings
                FROM reading_lists
                INNER JOIN books
                ON books.book_id=reading_lists.book_id
                INNER JOIN authors
                ON books.author_id=authors.author_id
                INNER JOIN reading_list_names
                ON reading_list_names.list_id=reading_lists.list_id
                WHERE reading_lists.list_id={list_id}
                    AND reading_lists.user_id={user_id}
                ORDER BY reading_lists.date_added DESC, books.title ASC;
            """.format(
                list_id=list_id,
                user_id=user_id  # This is not strictly necessary, but helps
                # protect against people being able to view other people's list
                # contents by guessing the list id.# Prevent any null values -
                # replace with 0s.
            )
        )

        queue = data_structures.Queue()
        for i in res:
            queue.push(i)

        list_name = self._connection.query("""
            SELECT list_name FROM reading_list_names
            WHERE list_id={};
        """.format(list_id))[0][0]  # See which list the button would move too.

        if list_name == "Currently Reading":
            button = "Mark as Read"
            move_target = self._connection.query("""
                SELECT list_id FROM reading_list_names
                WHERE list_name="Have Read"
                    AND user_id={};
            """.format(user_id))[0][0]
        elif list_name == "Want to Read":
            button = "Start Reading"
            move_target = self._connection.query("""
                SELECT list_id FROM reading_list_names
                WHERE list_name="Currently Reading"
                    AND user_id={};
            """.format(user_id))[0][0]
        else:
            button = None
            move_target = None

        output_dict = dict()
        for i in range(queue.size):
            k = queue.pop()
            author = components.authors.names_to_display(k[4], k[5], k[6])

            synopsis = "</p><p>".join(("<p>" + k[3] + "</p>").split("\n"))
            # Change new lines to new paragraphs
            output_dict[i] = {
                "id": k[0],
                "cover": k[1],
                "title": k[2],
                "synopsis": synopsis,
                "author": author,
                "author_id": k[7],
                "date_added": k[8].strftime("%d-%m-%Y"),
                "genres": k[9].split(",")[:self._num_display_genres],
                "average_rating": k[10],
                "num_reviews": k[11]
            }

        return output_dict, button, move_target

    def remove_entry(self, user_id, list_id, book_id):
        self._connection.query("""
        DELETE FROM reading_lists
        WHERE user_id={user_id}
            AND book_id={book_id}
            AND list_id={list_id};
        """.format(
            book_id=book_id,
            user_id=user_id,
            list_id=list_id
        ))

    def add_entry(self, user_id, list_id, book_id):
        self._recommendations.delete_recommendation(user_id, book_id, bad_recommendation=False)
        # Delete recommendation when added to a list

        books = {i[0] for i in self._connection.query("SELECT book_id FROM books")}
        users = {i[0] for i in self._connection.query("SELECT user_id FROM users")}

        if book_id in books and user_id in users:
            lists = {i[0] for i in self._connection.query("""
                SELECT list_id FROM reading_list_names
                WHERE list_name IN ("Currently Reading", "Have Read", "Want to Read")
                    AND user_id={}
            """.format(user_id))}

            if list_id in lists:
                self._connection.query("""
                    DELETE FROM reading_lists
                    WHERE user_id={user_id}
                        AND book_id={book_id}
                """.format(book_id=book_id, user_id=user_id))
                # Delete entry from other lists to prevent duplicates

            self._connection.query("""
                INSERT INTO reading_lists (user_id, book_id, list_id) VALUES 
                ({user_id}, {book_id}, {list_id});
            """.format(
                user_id=user_id,
                book_id=book_id,
                list_id=list_id
            ))

    def move_entry(self, user_id, start_list_id, end_list_id, book_id):
        self.add_entry(user_id, end_list_id, book_id)  # This changes the date
        # added, but this is not an issue as
        self.remove_entry(user_id, start_list_id, book_id)
        # as once moved, it would be a new addition to the list, so the date
        # should change.

    def remove_list(self, user_id, list_id):
        # Do not need to check whether the list is protected, the delete button
        # is hidden by the JS. To delete it would
        # still require session id, so cannot be done accidentally.
        self._connection.query("""
            DELETE FROM reading_lists
            WHERE list_id={list_id}
                AND user_id={user_id};
        """.format(list_id=list_id, user_id=user_id))
        # Only the specific users list will be deleted, as it targets the single
        # list

        self._connection.query("""
            DELETE FROM reading_list_names
            WHERE list_id={list_id}
                AND user_id={user_id}
        """.format(list_id=list_id, user_id=user_id))
        # Delete the list name

    def create_list(self, user_id, list_name):
        self._connection.query("""
            INSERT INTO reading_list_names (user_id, list_name) VALUES
            ({user_id}, "{list_name}")
        """.format(user_id=user_id, list_name=list_name))
    
    def get_most_recent_read(self, user_id):
        res = self._connection.query("""
            SELECT books.book_id,
                books.title
            FROM reading_lists
            INNER JOIN reading_list_names
                ON reading_lists.list_id=reading_list_names.list_id
            INNER JOIN books ON books.book_id=reading_lists.book_id
            WHERE reading_lists.user_id={}
                AND reading_list_names.list_name="Have Read"
            ORDER BY reading_lists.date_added DESC
            LIMIT 1;
        """.format(user_id))

        if len(res) > 0:
            return res[0]
        return None
    
    def get_newest_addition(self, user_id):
        res = self._connection.query("""
            SELECT books.book_id,
                books.title
            FROM reading_lists
            INNER JOIN reading_list_names
                ON reading_lists.list_id=reading_list_names.list_id
            INNER JOIN books ON books.book_id=reading_lists.book_id
            WHERE reading_lists.user_id={}
                AND reading_list_names.list_name!="Have Read"
            ORDER BY reading_lists.date_added DESC
            LIMIT 1;
        """.format(user_id))

        if len(res) > 0:
            return res[0]
        return None
