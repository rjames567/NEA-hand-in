# -----------------------------------------------------------------------------
# Standard Python library imports
# -----------------------------------------------------------------------------
import json
import urllib.parse

# -----------------------------------------------------------------------------
# Project imports
# -----------------------------------------------------------------------------
import components.accounts
import components.authors
import components.books
import components.diaries
import components.genres
import components.information_retrieval
import components.reading_lists
import components.recommendations

import configuration
import environ_manipulation
import logger
import mysql_handler

# -----------------------------------------------------------------------------
# Project constants
# -----------------------------------------------------------------------------
config = configuration.Configuration(
    "./project_config.conf",
    default_conf_filename="./default_config.json"
)
# The json does not need to be user editable, so is not very readable.

# -----------------------------------------------------------------------------
# Database connection
# -----------------------------------------------------------------------------
connection = mysql_handler.Connection(
    user=config.get("mysql username"),
    password=config.get("mysql password"),
    schema=config.get("mysql schema"),
    host=config.get("mysql host")
)

# -----------------------------------------------------------------------------
# Project Constants
# -----------------------------------------------------------------------------
number_home_summaries = config.get("home number_home_summaries")  # This is a
# constant, as is is used multiple times, and will always be faster to access as
# a variable, and otherwise, the get function would be have to run during the
# calling of methods as part of a response.

# -----------------------------------------------------------------------------
# Class instantiation
# -----------------------------------------------------------------------------
diaries = components.diaries.Diaries(connection)
genres = components.genres.Genres(connection)
sessions = components.accounts.Sessions(
    connection,
    config.get("session_id_length")
)
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
accounts = components.accounts.Accounts(
    connection,
    config.get("passwords hashing_algorithm"),
    config.get("passwords salt"),  # Stored in the config as binary
    config.get("passwords number_hash_passes"),
    reading_lists
)
information_retrieval = components.information_retrieval.DocumentCollection(
    connection,
    books,
    authors,
    genres,
    config.get("search number_results")
)


# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------
# Note that this is not technically a middleware as it is not totally
# transparent, but it performs the same role.
class Middleware(object):
    def __init__(self, routes, log):
        self._routes = routes
        self._log = log
        self._log.output_message(f"Create Middleware object")

    def __call__(self, environ, start_response):
        target_name = environ_manipulation.application.get_target(environ)
        self._log.output_message(f"Attempting to redirect to {target_name} application")
        target_application = self._routes.get(target_name) or ErrorHandler("404 Not Found", log)
        return target_application(environ, start_response)


# -----------------------------------------------------------------------------
# Handler Base Class
# -----------------------------------------------------------------------------
class Handler(object):
    def __init__(self, log):
        self._routes = {}  # There are no routes for the base class - included so the __call__ should still work
        self._log = log
        self._log.output_message("Created " + __class__.__name__ + " instance")  # Cannot use
        # commas as it the method only takes 2 parameters, and these would
        # pass each element as a parameter

    def retrieve_post_parameters(self):
        try:
            body_size = int(self._environ["CONTENT_LENGTH"])
        except ValueError:
            body_size = 0

        return self._environ["wsgi.input"].read(body_size).decode("utf-8")

    def retrieve_get_parameters(self):
        query = self._environ.get("QUERY_STRING")
        arr_dict = urllib.parse.parse_qs(query)  # Returns dictionary of arrays {str: list}
        res = {i: arr_dict[i][0] for i in arr_dict.keys()}  # Convert to dictionary {str: str}
        #  Use urllib as it handles the non-printable characters – %xx
        return res

    def __call__(self, environ, start_response):
        try:
            self._environ = environ  # Set so methods do not need to have it as a parameter.
            self._log.output_message(self.__class__.__name__ + " object called")
            self._log.output_message(f"     Handling request. URI: {self._environ['REQUEST_URI']}")
            target_name = environ_manipulation.application.get_sub_target(self._environ)
            self._log.output_message(f"     Redirecting to {self.__class__.__name__}.{target_name}")
            target_function = self._routes.get(target_name) or ErrorHandler("404 Not Found", log).error_response
            response, status, response_headers = target_function()
        except Exception as e:
            self._log.output_message(f"     An error occurred within {self.__class__.__name__}.{target_name} whilst processing the request")
            self._log.output_message("     " + repr(e))
            response, status, response_headers = ErrorHandler("500 Server Error", log).error_response()
        start_response(status, response_headers)
        self._log.output_message(f"     Response given.    status: {status}    headers: {response_headers}    response: {response}")
        yield response.encode("utf-8")


# -----------------------------------------------------------------------------
# Account Handler
# -----------------------------------------------------------------------------
class AccountHandler(Handler):
    def __init__(self, log):
        super().__init__(log)
        self._routes = {
            "sign_in": self.sign_in,
            "sign_out": self.sign_out,
            "sign_up": self.sign_up
        }

    def sign_in(self):
        # Method is already specified for log - redirecting to object.method
        json_response = self.retrieve_post_parameters()
        response_dict = json.loads(json_response)
        username = response_dict["username"]
        try:
            user_id = accounts.check_credentials(
                username=username,
                password=response_dict["password"]
            )
            session_id = sessions.create_session(user_id)
            message = "Signed in successfully"
            self._log.output_message("          Signed into account     Username: " + username)
            self._log.output_message("          Session id: " + session_id)
        except components.accounts.InvalidUserCredentialsError:
            self._log.output_message("          Failed to sign into account     Username: " + username)
            message = "Invalid username or password"
            session_id = None
            self._log.output_message("          Session id: #N/A")

        response = json.dumps({
            "message": message,
            "session_id": session_id
        })

        status = "200 OK"

        response_headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(response)))
        ]

        return response, status, response_headers

    def sign_out(self):
        session_id = self.retrieve_post_parameters()
        sessions.close(session_id)
        self._log.output_message("          Closed session     Session id: " + session_id)

        status = "200 OK"

        response = "true"  # Response is not needed – it is for completeness only. The client does not wait or respond.

        response_headers = [
            ("Content-Type", "text/plain"),
            ("Content-Length", str(len(response)))
        ]

        return response, status, response_headers

    def sign_up(self):
        json_response = self.retrieve_post_parameters()
        response_dict = json.loads(json_response)
        username = response_dict["username"]
        try:
            user_id = accounts.create_user(
                first_name=response_dict["first_name"],
                surname=response_dict["surname"],
                username=username,
                password=response_dict["password"]
            )
            session_id = sessions.create_session(user_id)
            message = "Account created successfully"
            self._log.output_message("          Created account     Username: " + username)
            self._log.output_message("          Session id: " + session_id)
        except components.accounts.UserExistsError:
            self._log.output_message("          Failed to create account - username is taken     Username: " + username)
            message = "Username is already taken."
            session_id = None  # json.dumps converts this to null automatically
            self._log.output_message("          Session id: N/A")

        response = json.dumps({
            "message": message,
            "session_id": session_id  # Success can be interpreted from the id
        })

        status = "200 OK"
        response_headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(response)))
        ]
        return response, status, response_headers


# -----------------------------------------------------------------------------
# My Books Handler
# -----------------------------------------------------------------------------
class MyBooksHandler(Handler):
    def __init__(self, log):
        super().__init__(log)
        self._routes = {
            "get_lists": self.get_list_names,
            "get_list_entries": self.get_list_entries,
            "remove_list_entry": self.remove_list_entry,
            "add_list_entry": self.add_list_entry,
            "move_list_entry": self.move_list_entry,
            "remove_list": self.remove_list,
            "create_list": self.create_list,
            "get_lists_book_target": self.get_list_names_include_book
        }

    def get_list_names(self):
        session_id = self.retrieve_get_parameters()["session_id"]
        self._log.output_message("          Session id: " + session_id)
        try:
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User id: " + str(user_id))

            names = reading_lists.get_names(user_id)
            response = json.dumps({i: names.pop() for i in range(names.size)})

            status = "200 OK"

            response_headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def get_list_entries(self):
        response_dict = self.retrieve_get_parameters()

        session_id = response_dict["session_id"]
        try:
            self._log.output_message("          Session id: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User id: " + str(user_id))

            list_id = response_dict["list_id"]
            self._log.output_message("          List ID: " + str(list_id))

            result = dict()

            result["books"], result["button"], result["move_target_id"] = reading_lists.get_values(list_id, user_id)

            if not len(result["books"]):
                result["meta"] = "You have no books in this list"
            else:
                result["meta"] = None

            response = json.dumps(result)  # Logging this will be slow – remove debug for production from config.

            status = "200 OK"

            response_headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def remove_list_entry(self):
        json_response = self.retrieve_post_parameters()
        response_dict = json.loads(json_response)
        session_id = response_dict["session_id"]
        list_id = response_dict["list_id"]
        book_id = response_dict["book_id"]  # Replace ampersand code with character

        try:
            self._log.output_message("          Session id: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User id: " + str(user_id))

            self._log.output_message("          List ID: " + str(list_id))
            self._log.output_message("          Book ID: " + str(book_id))

            reading_lists.remove_entry(user_id, list_id, book_id)
            response = "true"  # A response is needed to use this result, but does not impact the client at all.

            status = "200 OK"

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]

        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def move_list_entry(self):
        json_response = self.retrieve_post_parameters()
        response_dict = json.loads(json_response)
        session_id = response_dict["session_id"]
        list_id = response_dict["list_id"]
        book_id = response_dict["book_id"]

        try:
            self._log.output_message("          Session id: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User id: " + str(user_id))

            self._log.output_message("          List ID: " + str(list_id))
            self._log.output_message("          Book ID: " + str(book_id))

            target_list_id = response_dict["target_list_id"]
            self._log.output_message("          Target list ID: " + str(target_list_id))

            reading_lists.move_entry(user_id, list_id, target_list_id, book_id)

            response = "true"  # A response is needed to use this result, but does not impact the client at all.

            status = "200 OK"

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def remove_list(self):
        json_response = self.retrieve_post_parameters()
        response_dict = json.loads(json_response)
        session_id = response_dict["session_id"]
        list_id = response_dict["list_id"]

        try:
            self._log.output_message("          Session id: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User id: " + str(user_id))
            self._log.output_message("          List ID: " + str(list_id))

            reading_lists.remove_list(user_id, list_id)

            response = "true"  # A response is needed to use this result, but does not impact the client at all.

            status = "200 OK"

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def create_list(self):
        json_response = self.retrieve_post_parameters()
        response_dict = json.loads(json_response)
        session_id = response_dict["session_id"]
        list_name = response_dict["list_name"]

        try:
            self._log.output_message("          Session id: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User id: " + str(user_id))
            self._log.output_message("          List name: " + list_name)

            reading_lists.create_list(user_id, list_name)

            response = "true"  # A response is needed to use this result, but does not impact the client at all.

            status = "200 OK"

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def get_list_names_include_book(self):
        params = self.retrieve_get_parameters()
        session_id = params["session_id"]
        try:
            self._log.output_message("          Session id: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User id: " + str(user_id))
            book_id = params["book_id"]
            self._log.output_message("          Book id: " + str(book_id))

            result = reading_lists.get_names_check_book_in(user_id, book_id)

            response = json.dumps(result)

            status = "200 OK"

            response_headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def add_list_entry(self):
        params = self.retrieve_post_parameters()
        params = json.loads(params)
        session_id = params["session_id"]
        try:
            self._log.output_message("          Session id: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User id: " + str(user_id))
            book_id = params["book_id"]
            self._log.output_message("          Book id: " + str(book_id))
            list_id = params["list_id"]
            self._log.output_message("          List id: " + str(list_id))

            reading_lists.add_entry(user_id, list_id, book_id)

            response = "true"  # Response does not matter to the client

            status = "200 OK"

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers


# -----------------------------------------------------------------------------
# Genres Handler
# -----------------------------------------------------------------------------
class GenreHandler(Handler):
    def __init__(self, log):
        super().__init__(log)
        self._routes = {
            "about_data": self.get_genre_data
        }

    def get_genre_data(self):
        genre_name = self.retrieve_get_parameters()["genre_name"]
        self._log.output_message("          Genre name: " + genre_name)
        try:
            result = genres.get_about_data(genre_name)
            status = "200 OK"
            self._log.output_message("          Success")

            response = json.dumps(result)
            self._log.output_message("          Response: " + response)
            self._log.output_message("          Status: " + status)

            response_headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(response)))
            ]

            return response, status, response_headers

        except components.genres.GenreNotFoundError:
            status = "404 Not Found"
            self._log.output_message("          Status: " + status)
            return ErrorHandler("404 Not Found", self._log).error_response()  # Return the content for a 404 error


# -----------------------------------------------------------------------------
# Book Handler
# -----------------------------------------------------------------------------
class BookHandler(Handler):
    def __init__(self, log):
        super().__init__(log)
        self._routes = {
            "about_data": self.get_book_data,
            "delete_review": self.delete_review,
            "add_review": self.leave_review
        }

    def get_book_data(self):
        get_params = self.retrieve_get_parameters()
        session_id = get_params["session_id"]
        book_id = get_params["book_id"]
        self._log.output_message("          Book ID: " + book_id)
        self._log.output_message("          Session ID: " + session_id)
        
        try:
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
        except components.accounts.SessionExpiredError:
            user_id = None
            self._log.output_message("          Session expired / No session")
        self._log.output_message("          User ID: " + str(user_id))
        try:
            result = books.get_about_data(book_id, user_id)

            result["similar_books"] = books.get_similar_items(int(book_id))
            status = "200 OK"
            self._log.output_message("          Success")

            response = json.dumps(result)
            # self._log.output_message("          Response: " + response)
            self._log.output_message("          Status: " + status)

            response_headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(response)))
            ]

            return response, status, response_headers

        except components.books.BookNotFoundError:
            status = "404 Not Found"
            self._log.output_message("          Status: " + status)
            return ErrorHandler("404 Not Found", self._log).error_response()  # Return the content for a 404 error

    def delete_review(self):
        json_response = self.retrieve_post_parameters()
        params = json.loads(json_response)
        session_id = params["session_id"]
        review_id = params["review_id"]
        self._log.output_message("          Review ID: " + str(review_id))
        try:
            self._log.output_message("          Session ID: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))

            books.delete_review(review_id, user_id)  # This is accounted for in the fit method.

            response = "true"  # A response is needed to use this result, but does not impact the client at all.

            status = "200 OK"

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def leave_review(self):
        json_response = self.retrieve_post_parameters()
        params = json.loads(json_response)
        try:
            session_id = params["session_id"]
            self._log.output_message("          Session ID: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))
            book_id = params["book_id"]
            self._log.output_message("          Book ID: " + str(book_id))

            books.leave_review(
                user_id,
                book_id,
                params["overall_rating"],
                params["plot_rating"],
                params["character_rating"],
                params["summary"],
                params["thoughts"]
            )

            list_id = reading_lists.get_list_id("Have Read", user_id)
            reading_lists.add_entry(user_id, list_id, book_id)

            # This will be included in the recommendations fit

            response = "true"  # A response is needed to use this result, but does not impact the client at all.

            status = "200 OK"

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers


# -----------------------------------------------------------------------------
# Author Handler
# -----------------------------------------------------------------------------
class AuthorHandler(Handler):
    def __init__(self, log):
        super().__init__(log)
        self._routes = {
            "follow_author": self.follow_author,
            "unfollow_author": self.unfollow_author,
            "about_data": self.get_author_data
        }

    def follow_author(self):
        json_response = self.retrieve_post_parameters()
        params = json.loads(json_response)
        session_id = params["session_id"]
        author_id = params["author_id"]
        try:
            self._log.output_message("          Author ID: " + str(author_id))
            self._log.output_message("          Session ID: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))

            authors.follow(user_id, author_id)

            response = str(authors.get_number_followers(author_id))  # Sends the new number of followers as the response.
            # Cast the integer result to string so it can be sent as text.

            status = "200 OK"

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def unfollow_author(self):
        json_response = self.retrieve_post_parameters()
        params = json.loads(json_response)
        session_id = params["session_id"]
        author_id = params["author_id"]
        try:
            self._log.output_message("          Author ID: " + str(author_id))
            self._log.output_message("          Session ID: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))

            authors.unfollow(user_id, author_id)

            response = str(authors.get_number_followers(author_id))  # Sends the new amount followers as the response.
            # Cast the integer result to string, so it can be sent as text.

            status = "200 OK"

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def get_author_data(self):
        get_params = self.retrieve_get_parameters()
        author_id = get_params["author_id"]
        self._log.output_message("          Author ID: " + str(author_id))
        try:
            result = authors.get_about_data(author_id)
            status = "200 OK"
            self._log.output_message("          Success")

            response = json.dumps(result)
            self._log.output_message("          Response: " + response)
            self._log.output_message("          Status: " + status)

            response_headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(response)))
            ]

            return response, status, response_headers

        except components.authors.AuthorNotFoundError:
            status = "404 Not Found"
            self._log.output_message("          Status: " + status)
            return ErrorHandler("404 Not Found", self._log).error_response()  # Return the content for a 404 error


# -----------------------------------------------------------------------------
# Diary Handler
# -----------------------------------------------------------------------------
class DiaryHandler(Handler):
    def __init__(self, log):
        super().__init__(log)
        self._routes = {
            "get_entries": self.get_entries,
            "delete_entry": self.delete_entry,
            "add_entry": self.add_entry
        }

    def get_entries(self):
        session_id = self.retrieve_get_parameters()["session_id"]  # Only has one parameter, so this is fine.
        try:
            self._log.output_message("          Session ID: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))

            result = {
                "entries": diaries.get_entries(user_id),
                "books": reading_lists.get_currently_reading(user_id)
            }
            
            response = json.dumps(result)

            status = "200 OK"

            self._log.output_message("          Response: " + response)
            self._log.output_message("          Status: " + status)

            response_headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def delete_entry(self):
        json_response = self.retrieve_post_parameters()
        params = json.loads(json_response)
        try:
            session_id = params["session_id"]
            entry_id = params["entry_id"]
            self._log.output_message("          Entry ID: " + str(entry_id))
            self._log.output_message("          Session ID: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))

            diaries.delete_entry(user_id, entry_id)

            response = "true"  # The client does not need the response. This is just for completeness, and a value is
            # required for the return statement.

            status = "200 OK"

            self._log.output_message("          Response: " + response)
            self._log.output_message("          Status: " + status)

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def add_entry(self):
        json_response = self.retrieve_post_parameters()
        params = json.loads(json_response)
        session_id = params["session_id"]
        book_id = params["book_id"]
        try:
            self._log.output_message("          Session ID: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))
            self._log.output_message("          Book ID: " + str(book_id))

            diaries.add_entry(
                user_id,
                book_id,
                params["overall_rating"],
                params["character_rating"],
                params["plot_rating"],
                params["summary"],
                params["thoughts"],
                params["pages_read"]
            )

            if params["book_completed"]:
                list_id = reading_lists.get_list_id("Have Read", user_id)
                reading_lists.add_entry(user_id, list_id, book_id)

                if params["as_review"]:
                    books.leave_review(
                        user_id,
                        book_id,
                        params["overall_rating"],
                        params["plot_rating"],
                        params["character_rating"],
                        params["summary"],
                        params["thoughts"]
                    )

            response = "true" # The response does not matter - here for completeness only

            status = "200 OK"

            self._log.output_message("          Response: " + response)
            self._log.output_message("          Status: " + status)

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers


# -----------------------------------------------------------------------------
# Home Handler
# -----------------------------------------------------------------------------
class HomeHandler(Handler):
    def __init__(self, log):
        super().__init__(log)
        self._routes = {
            "get_data": self.get_data
        }
    
    def get_data(self):
        session_id = self.retrieve_get_parameters()["session_id"]  # Only has one parameter, so this is fine.
        result = dict()
        try:
            self._log.output_message("          Session ID: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))

            result["recommended"] = recommendations.get_user_recommendation_summaries(user_id)[:number_home_summaries]
            result["currently_reading"] = reading_lists.get_currently_reading(user_id)[:number_home_summaries]
            result["want_read"] = reading_lists.get_want_read(user_id)[:number_home_summaries]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired / No session")
            result["recommended"] = None
            result["currently_reading"] = None
            result["want_read"] = None
        
        result["trending"] = reading_lists.get_popular()
        result["newest_additions"] = books.get_newest()

        response = json.dumps(result)

        status = "200 OK"

        self._log.output_message("          Response: " + response)
        self._log.output_message("          Status: " + status)

        response_headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(response)))
        ]

        return response, status, response_headers


# -----------------------------------------------------------------------------
# Recommendations Handler
# -----------------------------------------------------------------------------
class RecommendationsHandler(Handler):
    def __init__(self, log):
        super().__init__(log)
        self._routes = {
            "get_recommendations": self.get_user_recommendations,
            "remove_recommendation": self.remove_user_recommendation,
            "add_list_entry": self.add_to_want_read,
            "set_user_preferences": self.set_new_user_preferences
        }
    
    def get_user_recommendations(self):
        session_id = self.retrieve_get_parameters()["session_id"]  # Only has one parameter, so this is fine.
        self._log.output_message("          Session ID: " + session_id)
        try:
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))

            result = dict()
            try:
                result["data"] = recommendations.get_user_recommendations(user_id)
                result["new_user"] = False
                result["list_id"] = reading_lists.get_list_id("Want to Read", user_id)  # This is not needed if it
                # is a new user.
            except components.recommendations.NoUserPreferencesError:
                result["data"] = authors.get_author_id_list(names=True)
                result["new_user"] = True

            response = json.dumps(result)

            status = "200 OK"

            self._log.output_message("          Response: " + response)
            self._log.output_message("          Status: " + status)

            response_headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def remove_user_recommendation(self):
        json_response = self.retrieve_post_parameters()
        params = json.loads(json_response)
        session_id = params["session_id"]
        book_id = params["book_id"]
        try:
            self._log.output_message("          Session ID: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))
            self._log.output_message("          Book ID: " + str(book_id))

            recommendations.delete_recommendation(user_id, book_id)  # This includes the impact to the recommendation model

            response = "true" # The response does not matter - here for completeness only

            status = "200 OK"

            self._log.output_message("          Response: " + response)
            self._log.output_message("          Status: " + status)

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def add_to_want_read(self):
        json_response = self.retrieve_post_parameters()
        params = json.loads(json_response)
        session_id = params["session_id"]
        try:
            book_id = params["book_id"]
            self._log.output_message("          Session ID: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))
            self._log.output_message("          Book ID: " + str(book_id))
            list_id = params["list_id"]
            self._log.output_message("          List id: " + str(list_id))

            reading_lists.add_entry(user_id, list_id, book_id)  # Removal of recommendation is included in the add_entry

            response = "true" # The response does not matter - here for completeness only

            status = "200 OK"

            self._log.output_message("          Response: " + response)
            self._log.output_message("          Status: " + status)

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers

    def set_new_user_preferences(self):
        json_response = self.retrieve_post_parameters()
        params = json.loads(json_response)
        try:
            session_id = params["session_id"]
            author_ids = params["authors"]
            self._log.output_message("          Session ID: " + session_id)
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))
            recommendations.add_user(user_id, [int(i) for i in author_ids])  # author_ids is returned as a list
            # of strings. This also generates and stores the recommendations.

            response = "true"  # The response does not matter - here for completeness only

            status = "200 OK"

            self._log.output_message("          Response: " + response)
            self._log.output_message("          Status: " + status)

            response_headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(response)))
            ]
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            response = "false"

            status = "403 forbidden"

            response_headers = [
                ("Content-Type", "text/plain")
            ]

        return response, status, response_headers


# -----------------------------------------------------------------------------
# Searching Handler
# -----------------------------------------------------------------------------
class SearchingHandler(Handler):
    def __init__(self, log):
        super().__init__(log)
        self._routes = {
            "search": self.search_database,
            "get_browse_data": self.get_browse_data
        }

    def search_database(self):
        query = self.retrieve_get_parameters()["query"]  # Only has one parameter, so this is fine.
        self._log.output_message("          Query: " + query)
        result = information_retrieval.database_search(query)

        response = json.dumps(result)

        status = "200 OK"

        self._log.output_message("          Response: " + response)
        self._log.output_message("          Status: " + status)

        response_headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(response)))
        ]

        return response, status, response_headers
    
    def get_browse_data(self):
        session_id = self.retrieve_get_parameters()["session_id"]
        self._log.output_message("          Session ID: " + session_id)
        try:
            user_id = sessions.get_user_id(session_id)
            sessions.update_time(session_id)
            self._log.output_message("          User ID: " + str(user_id))
        except components.accounts.SessionExpiredError:
            self._log.output_message("          Session expired")
            user_id = None
            self._log.output_message("          User ID: #N/A")
        
        result = {
            "trending": reading_lists.get_popular(),
            "newest_additions": books.get_newest(),
            "highly_rated": books.get_highly_rated()
        }  # This is not user specific

        result["because_read"] = result["because_added"] = None

        if user_id is not None:
            res = reading_lists.get_most_recent_read(user_id)
            if res is not None:
                book_id, title = res
                if book_id is not None:
                    result["because_read"] = books.get_similar_items(book_id)
                    result["because_read_title"] = title
            res = reading_lists.get_newest_addition(user_id)
            if res is not None:
                book_id, title = res
                if book_id is not None:
                    result["because_added"] = books.get_similar_items(book_id)
                    result["because_added_title"] = title
            result["favourite_authors"] = authors.get_author_favourite_data(user_id)
            
        response = json.dumps(result)

        status = "200 OK"

        self._log.output_message("          Response: " + response)
        self._log.output_message("          Status: " + status)

        response_headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(response)))
        ]

        return response, status, response_headers


# -----------------------------------------------------------------------------
# Error Handler
# -----------------------------------------------------------------------------
class ErrorHandler(Handler):
    def __init__(self, status, log):
        super().__init__(log)
        self._status = status

    def error_response(self):
        self._log.output_message(f"     Handling error: {self._status}")
        response = f"<h1>{self._status}</h1>"
        if self._status[0] == "4":  # Other messages are successful, so do not need to be created.
            response += "<p>The page you were looking for does not exist.</p>"
        elif self._status[0] == "5":
            response += "<p>A server error has occurred. Please try again later.</p>"

        response_headers = [
            ("Content-Type", "text/html")
        ]

        return response, self._status, response_headers  # Status is needed as this format is needed elsewhere

    def __call__(self, environ, start_response):
        self._log.output_message(self.__class__.__name__ + " object called")
        self._log.output_message(f"     Handling request. URI: {environ['REQUEST_URI']}")
        response, status, response_headers = self.error_response()  # Overwrite standard method. Different to reduce
        # necessary processing – it is known an error has occurred, it does not need to be checked for.
        start_response(status, response_headers)
        self._log.output_message(f"     Response given.    status: {self._status}    headers: {response_headers}    response: {response}")
        yield response.encode("utf-8")


# -----------------------------------------------------------------------------
# File execution
# -----------------------------------------------------------------------------
if __name__ != "__main__":
    log = logger.Logging(debugging=config.get("debugging"))

    # https://www.sitepoint.com/python-web-applications-the-basics-of-wsgi/
    routes = {
        "account": AccountHandler(log),
        "my_books": MyBooksHandler(log),
        "genres": GenreHandler(log),
        "books": BookHandler(log),
        "authors": AuthorHandler(log),
        "diary": DiaryHandler(log),
        "home": HomeHandler(log),
        "recommendations": RecommendationsHandler(log),
        "search": SearchingHandler(log)
        # Objects are persistent, so will the response should be faster and more memory efficient.
    }

    app = Middleware(routes, log)
