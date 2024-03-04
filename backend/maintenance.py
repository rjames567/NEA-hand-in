# -----------------------------------------------------------------------------
# Project imports
# -----------------------------------------------------------------------------
import components.accounts
import components.recommendations

import configuration
import mysql_handler

# -----------------------------------------------------------------------------
# Project constants
# -----------------------------------------------------------------------------
config = configuration.Configuration("./project_config.conf", default_conf_filename="./default_config.json")

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
# Class instantiation
# -----------------------------------------------------------------------------
sessions = components.accounts.Sessions(
    connection,
    config.get("session_id_length")
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

# -----------------------------------------------------------------------------
# Sessions
# -----------------------------------------------------------------------------
for i in sessions.get_session_id_list():
    try:
        sessions.get_user_id(i)
    except components.accounts.SessionExpiredError:
        pass

# -----------------------------------------------------------------------------
# Recommendations
# -----------------------------------------------------------------------------
recommendations.fit()
recommendations.gen_recommendations()
