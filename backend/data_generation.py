import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
print("Started Imports 1/11")
import json
import random

# from gensim.summarization.summarizer import summarize
# from gensim.summarization import keywords

import components.accounts
import components.authors
import components.books
import components.genres
import components.information_retrieval
import components.recommendations

import configuration
import mysql_handler

print("Finished Imports 1/11")

# -----------------------------------------------------------------------------
# Object instantiation
# -----------------------------------------------------------------------------
print("Started object instantiation 2/11")
config = configuration.Configuration("./project_config.conf", "./default_config.json")
connection = mysql_handler.Connection(
    user=config.get("mysql username"),
    password=config.get("mysql password"),
    schema=config.get("mysql schema"),
    host=config.get("mysql host")
)

accounts = components.accounts.Accounts(
        connection,
        config.get("passwords hashing_algorithm"),
        config.get("passwords salt"),
        config.get("passwords number_hash_passes"),
        None  # Reading lists object is not used, so passing None is safe.
    )

print("Finished object instantiation 2/11")

# -----------------------------------------------------------------------------
# Database clearing
# -----------------------------------------------------------------------------
# Set the query size limit - https://wp-staging.com/docs/increase-max_allowed_packet-size-in-mysql/#How_to_Set_max_allowed_packet_Temporary
# SET GLOBAL max_allowed_packet=1073741824; - this does not work through the connector, and must be done as root

print("Started database clearing 3/11")

with open("./MySQL/create_tables.sql", "r") as f:
    queries = f.read().split(";")

for i in queries:
    connection.query(i)

print("Finished database clearing 3/11")

# -----------------------------------------------------------------------------
# Authors
# -----------------------------------------------------------------------------
print("Started authors 4/11")
new_file = ""
isbn_lookup = dict()

with open("data/Original/metadata.json", "r") as f:
    query = "INSERT INTO authors (author_id, clean_name, first_name, surname, about) VALUES\n"

    file = f.readlines()

    authors = set()
    for i, line in enumerate(file):
        data = json.loads(line)
        authors.add(data["authors"].split(", ")[0])

    author_lookup = dict()
    for i, k in enumerate(authors):  # Set makes items unique
        if i != 0:
            query += ",\n"
        author_lookup[k] = i + 1
        clean_name = components.information_retrieval.clean_data(k)
        query += f'({i + 1}, "{clean_name}", "{k}", "", "This author does not have an about")'

    for i, line in enumerate(file):
        data = json.loads(line)
        data["authors"] = author_lookup[data["authors"].split(", ")[0]]
        isbn_lookup[data['item_id']] = i + 1
        new_file += json.dumps(data) + "\n"
    query += ";"
    connection.query(query)

with open("data/metadata-altered.json", "w+") as f:
    f.write(new_file)

with open("data/Original/survey_answers.json") as f:
    with open("data/survey_answers.json", "w+") as k:
        for line in f:
            data = json.loads(line)
            try:
                book = isbn_lookup[data["item_id"]]
                data.pop("item_id")
                data["book_id"] = book
                if data["score"] == -1:
                    data["score"] = 0
                k.write(json.dumps(data) + "\n")
            except KeyError:
                pass


del query
del new_file
del f
del author_lookup
del file

print("Finished authors 4/11")

# -----------------------------------------------------------------------------
# books
# -----------------------------------------------------------------------------
print("Started books 5/11")
new_file = ""

with open("data/metadata-altered.json", "r") as f:
    query = "INSERT INTO books (book_id, author_id, title, clean_title, synopsis, cover_image, purchase_link, fiction, release_date, isbn) VALUES\n"
    for i, line in enumerate(f):
        if i != 0:
            query += ",\n"
        data = json.loads(line)
        if data['year'] != "0000":
            if type(data['description']) == float:
                synopsis = ""
            else:
                # https://pythonguides.com/remove-unicode-characters-in-python/
                synopsis = data["description"].encode("ascii", "ignore").decode().replace('"', "'").replace(";", "")
            title = data["title"].encode("ascii", "ignore").decode().replace('"', "'")
            query += '({book_id}, {author_id}, "{book_title}", "{clean_title}", "{synopsis}", "{cover_image}", "{link}", true, "{release_date}", "{isbn}")'.format(
                book_id=i + 1,
                author_id=data['authors'],
                book_title=title,
                clean_title=components.information_retrieval.clean_data(title),
                synopsis=synopsis.replace('"', "'"),  # .replace("\n", "\\n"),
                cover_image=data['img'],
                link=data['url'],
                release_date=str(data['year']) + "-01-01 " + " 00:00:00",
                isbn=data['item_id']
            )
    query += ";"
    connection.query(query)

with open("data/metadata-altered.json", "w+") as f:
    f.write(new_file)

del query
del new_file
del f
print("Finished books 5/11")

# -----------------------------------------------------------------------------
# Users
# -----------------------------------------------------------------------------
print("Started users 6/11")
query1 = "INSERT INTO users (user_id, username, password_hash, first_name, surname, preferences_set) VALUES\n"
query2 = "INSERT INTO reading_list_names (list_id, user_id, list_name) VALUES\n"
query3 = "INSERT INTO reading_lists (entry_id, list_id, book_id, user_id) VALUES\n"
prev = None
count = 1
for i in range(1, 601):
    if i != 1:
        query1 += ",\n"
        query2 += ",\n"
    query1 += '({num}, "user{num}", "5d557544916fde5c6b162cfcbce84181fb2cbe8798439b643edf96ee4c5826b4", "f{num}", "s{num}", TRUE)'.format(
        num=i)  # Password is password
    # preferences set is TRUE, so recommendations can be made to these users immediately.
    query2 += '({list}, {user}, "Want to Read"),'.format(list=((i - 1) * 3) + 1, user=i)
    query2 += '({list}, {user}, "Currently Reading"),'.format(list=((i - 1) * 3) + 2, user=i)
    query2 += '({list}, {user}, "Have Read")'.format(list=((i - 1) * 3) + 3, user=i)
    available = list(range(1, 501))
    # if i != prev:
    #     query3 += ""
    for k in range(30):
        chance = random.randint(1, 10)
        book = random.choice(available)
        available.remove(book)
        if chance == 1:
            query3 += '({count}, {num}, {book}, {user})'.format(count=count, num=((i - 1) * 3) + 1, book=book, user=i)
            query3 += ",\n"
            count += 1
        elif chance == 2:
            query3 += '({count}, {num}, {book}, {user})'.format(count=count, num=((i - 1) * 3) + 2, book=book, user=i)
            query3 += ",\n"
            count += 1
        elif chance == 3:
            query3 += '({count}, {num}, {book}, {user})'.format(count=count, num=((i - 1) * 3) + 3, book=book, user=i)
            query3 += ",\n"
            count += 1

query1 += ";"
query2 += ";"
query3 = query3[:-2] + ";"
connection.query(query1)
connection.query(query2)
connection.query(query3)
print("Finished users 6/11")

# -----------------------------------------------------------------------------
# Reviews
# -----------------------------------------------------------------------------
print("Started reviews 7/11")
query = "INSERT INTO reviews (user_id, book_id, summary, overall_rating, character_rating, plot_rating, rating_body) VALUES\n"
with open("data/Original/reviews.json", "r") as f:
    # https://www.turing.com/kb/5-powerful-text-summarization-techniques-in-python
    prev = None
    available = list(range(1, 601))
    for i, line in enumerate(f):
        #        if i != 0 and len(available) > 1:
        #            query += ",\n"
        while line[-2] != '}':
            line += f.readline()
        data = json.loads(line)
        # https://pythonguides.com/remove-unicode-characters-in-python/
        body = data["txt"].encode("ascii", "ignore").decode().replace('"', "'").replace(";", "").replace("\\", "")

        if data['item_id'] != prev:
            available = list(range(1, 601))
            prev = data['item_id']

        if body == "":
            body = summary = "null"
        else:
            try:
                # summary = summarize(body, word_count=50)
                summary = "This is the summary"
                # summary = body
                body = '"' + body + '"'
            except ValueError:
                summary = body
                body = "null"

        if len(available):
            user_id = random.choice(available)
            available.remove(user_id)

            overall_rating = random.randint(0, 5)
            if random.randint(0, 1):
                character_rating = random.randint(0, 5)
            else:
                character_rating = "null"
            if random.randint(0, 1):
                plot_rating = random.randint(0, 5)
            else:
                plot_rating = "null"
            query += '({user_id}, {book_id}, "{summary}", {overall_rating}, {character_rating}, {plot_rating}, {rating_body})'.format(
                user_id=user_id,
                book_id=data['item_id'],
                summary=summary,
                overall_rating=overall_rating,
                character_rating=character_rating,
                plot_rating=plot_rating,
                rating_body=body  # .replace("\n", "\\n")
            )
            query += ","
    query = query[:-1] + ";"
    connection.query(query)
print("Finished reviews 7/11")

# -----------------------------------------------------------------------------
# Genres
# -----------------------------------------------------------------------------
print("Started genres 8/11")
with open("data/Original/tags.json", "r") as f:
    query = "INSERT INTO genres (genre_id, name, clean_name, about) VALUES\n"
    for i, line in enumerate(f):
        if i != 0:
            query += ",\n"
        data = json.loads(line)
        tag = data["tag"].replace('"', "'").title()
        newTag = ""
        for i in tag.split(" "):
            if len(newTag) > 0:
                newTag += " "
            temp = set(list(i.lower()))  # Get all unique values in string
            if len(temp) == 1 and i[0].lower() == "i":  # If the set has only one item, the first item of i will be that value
                newTag += i.upper()
            else:
                newTag += i  # Ensure that II, will be uppercase, for genres like World War I and World War II
        clean = components.information_retrieval.clean_data(newTag)
        query += '({id}, "{tag}", "{clean}", "This genre does not have an about")'.format(id=data["id"] + 1, tag=newTag, clean=clean)
    query += ";"

connection.query(query)

connection.query("""DROP TABLE IF EXISTS temp;""")
connection.query("""DELETE FROM book_genres;""")
connection.query("""CREATE TABLE temp (genre_id INT, score INT, book_id INT);""")

query = "INSERT INTO temp VALUES\n"
with open("data/survey_answers.json", "r") as f:
    for i, line in enumerate(f):
        if i != 0:
            query += ",\n"
        data = json.loads(line)
        query += '({tag}, {score}, {book})'.format(tag=data["tag_id"]+1, score=data["score"], book=data["book_id"]*2)
query += ";"

connection.query(query)

books = [i[0] for i in connection.query("SELECT book_id FROM books")]
query = "INSERT INTO book_genres (genre_id, book_id, match_strength) VALUES\n"
for j, i in enumerate(books):
    res = connection.query("""SELECT genre_id,
        AVG(score)/5 AS rating
        FROM temp
        WHERE book_id={}
        GROUP BY genre_id;
    """.format(i))

    for b, k in enumerate(res):
        if k[1] > 0:
            query += f"({k[0]}, {i}, {float(k[1])}),\n"
query = query[:-2] + ";"

connection.query(query)
        
connection.query("""DROP TABLE temp""")

connection.query("""DELETE FROM reviews WHERE book_id NOT IN (SELECT book_id FROM book_genres)""")
connection.query("""DELETE FROM reading_lists WHERE book_id NOT IN (SELECT book_id FROM book_genres)""")
connection.query("""DELETE FROM recommendations WHERE book_id NOT IN (SELECT book_id FROM book_genres)""")
connection.query("""DELETE FROM diary_entries WHERE book_id NOT IN (SELECT book_id FROM book_genres)""")
connection.query("""DELETE FROM books WHERE book_id NOT IN (SELECT book_id FROM book_genres)""")  # Remove books that do not have genres
print("Finished genres 8/11")

# -----------------------------------------------------------------------------
# TF-IDF search
# -----------------------------------------------------------------------------
print("Started IDF generation 11/11")
number_home_summaries = config.get("home number_home_summaries")
diaries = components.diaries.Diaries(connection)
genres = components.genres.Genres(connection)
sessions = components.accounts.Sessions(
    connection,
    config.get("session_id_length")
)
temp_authors = components.authors.Authors(
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
temp_books = components.books.Books(
    connection,
    reading_lists,
    config.get("home number_about_similarities"),
    number_home_summaries,
    config.get("number_display_genres")
)
accounts = components.accounts.Accounts(
    connection,
    config.get("passwords hashing_algorithm"),
    config.get("passwords salt"),  # Stored in the config as binary
    config.get("passwords number_hash_passes"),
    reading_lists
)
document = components.information_retrieval.DocumentCollection(
    connection,
    books,
    authors,
    genres,
    config.get("search number_results")
)

document.gen_idf_values()
print("Finished IDF generation 11/11")


# -----------------------------------------------------------------------------
# Prevent multiple reviews for each user
# -----------------------------------------------------------------------------
users = [i[0] for i in connection.query("SELECT user_id FROM users")]

for i in users:
    res = [i[0] for i in connection.query("""
        SELECT book_id
        FROM reviews
        WHERE user_id={}
    """.format(i))]

    for book in res:
        ids = [str(i[0]) for i in connection.query("SELECT review_id FROM reviews WHERE user_id={user} and book_id={books}".format(user=i, books=book))][1:]
        if len(ids):
            connection.query(f"DELETE FROM reviews WHERE review_id IN ({','.join(ids)})")
    
# -----------------------------------------------------------------------------
# Add reviews to the have read list
# -----------------------------------------------------------------------------
for i in users:
    books = [i[0] for i in connection.query("""
                SELECT book_id
                FROM reviews
                WHERE user_id={}
        """.format(i))]

    used = {i[0] for i in connection.query("""
        SELECT reading_lists.book_id
        FROM reading_lists
        INNER JOIN reading_list_names
            ON reading_lists.list_id=reading_list_names.list_id
        WHERE reading_list_names.list_name="Have Read"
            AND reading_list_names.user_id={}
        """.format(i))}
    
    list_id = connection.query("SELECT list_id FROM reading_list_names WHERE list_name='Have Read' AND user_id={}".format(i))

    query = "INSERT INTO reading_lists (list_id, book_id, user_id) VALUES "
    for k in books:
        print(list_id[0])
        if k not in used:
            query += f"({list_id[0][0]}, {k}, {i}),"
    connection.query(query[:-1])

# -----------------------------------------------------------------------------
# Recommendations
# -----------------------------------------------------------------------------
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
# This needs to be later, as the number of genres would be incorrect if it were done at the start

print("Started user preference generation 9/11")
recommendations.fit()
print("Finished user preference generation 9/11")

print("Started user recommendation generation 10/11")
recommendations.gen_recommendations()
print("Finished user recommendation generation 10/11")