SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
-- Makes it so order of table creation / deletion does not matter

-- -----------------------------------
-- Authors
-- -----------------------------------
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS author_followers;

CREATE TABLE authors (
    author_id INT NOT NULL AUTO_INCREMENT,
    first_name TINYTEXT,
    surname TINYTEXT,
    alias TINYTEXT,
    about TEXT,
    clean_name TINYTEXT NOT NULL,
    PRIMARY KEY (author_id)
);

CREATE TABLE author_followers (
    follow_id INT NOT NULL AUTO_INCREMENT,
    author_id INT NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (follow_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- -----------------------------------
-- Users
-- -----------------------------------
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    first_name TINYTEXT NOT NULL,
    surname TINYTEXT NOT NULL,
    username TINYTEXT NOT NULL,
    password_hash TINYTEXT NOT NULL,
    preferences_set BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (user_id)
);
-- Username should have a unique constraint, but it is not possible to add a
-- unique constraint to a TINYTEXT but varchar are slow so no unique constraint

-- -----------------------------------
-- Genre
-- -----------------------------------
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS book_genres;

CREATE TABLE genres (
    genre_id INT NOT NULL AUTO_INCREMENT,
    name TINYTEXT NOT NULL,
    about TEXT,
    clean_name TINYTEXT NOT NULL,
    PRIMARY KEY (genre_id)
);
-- Name should have a unique constraint, but it is not possible to add a unique
-- constraint to a TINYTEXT but varchar are slow so no unique constraint

CREATE TABLE book_genres (
    link_id INT NOT NULL AUTO_INCREMENT,
    book_id INT NOT NULL,
    genre_id INT NOT NULL,
    match_strength FLOAT NOT NULL,
    PRIMARY KEY (link_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

-- -----------------------------------
-- Recommendations
-- -----------------------------------
DROP TABLE IF EXISTS recommendations;
DROP TABLE IF EXISTS initial_preferences;
DROP TABLE IF EXISTS bad_recommendations;

CREATE TABLE recommendations (
    recommendation_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    certainty FLOAT NOT NULL,
    PRIMARY KEY (recommendation_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

CREATE TABLE initial_preferences (
    preference_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (preference_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

CREATE TABLE bad_recommendations (
    recommendation_id INT NOT NULL auto_increment,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (recommendation_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- -----------------------------------
-- Books
-- -----------------------------------
DROP TABLE IF EXISTS books;

CREATE TABLE books (
    book_id INT NOT NULL AUTO_INCREMENT,
    author_id INT NOT NULL,
    title TINYTEXT NOT NULL,
    clean_title TINYTEXT NOT NULL,
    synopsis TEXT NOT NULL,
    cover_image TINYTEXT NOT NULL,
    purchase_link TINYTEXT NOT NULL,
    fiction BOOL NOT NULL,
    release_date DATE NOT NULL,
    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    isbn TINYTEXT NOT NULL, -- TINYTEXT to avoid issues with leading 0s
    PRIMARY KEY (book_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);
-- cover_image, purchase_link and isbn should have a unique constraint, but it
-- is not possible to add a unique constraint to a TINYTEXT but varchar are
-- slow so no unique constraint

-- -----------------------------------
-- Reading Lists
-- -----------------------------------
DROP TABLE IF EXISTS reading_lists;
DROP TABLE IF EXISTS reading_list_names;

CREATE TABLE reading_lists (
    entry_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    list_id INT NOT NULL,
    PRIMARY KEY (entry_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (list_id) REFERENCES reading_list_names(list_id)
);

CREATE TABLE reading_list_names (
    list_id INT NOT NULL AUTO_INCREMENT,
    list_name TINYTEXT NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (list_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
-- On creation of new user, the standard lists need to be created manually
-- due to the lack of support for triggers with pythonanywhere.com.

-- -----------------------------------
-- Diary Entries
-- -----------------------------------
DROP TABLE IF EXISTS diary_entries;

CREATE TABLE diary_entries (
    entry_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    overall_rating INT NOT NULL,
    character_rating INT,
    plot_rating INT,
    summary TINYTEXT,
    thoughts TEXT,
    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pages_read INT NOT NULL DEFAULT 0,
    PRIMARY KEY (entry_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- -----------------------------------
-- Review
-- -----------------------------------
DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews (
    review_id INT NOT NULL AUTO_INCREMENT,
    book_id INT NOT NULL,
    user_id INT NOT NULL,
    summary TEXT,
    overall_rating INT NOT NULL,
    plot_rating INT,
    character_rating INT,
    rating_body TEXT,
    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (review_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- -----------------------------------
-- Session IDs
-- -----------------------------------
DROP TABLE IF EXISTS sessions;

CREATE TABLE sessions (
    entry_id INT NOT NULL AUTO_INCREMENT,
    client_id TEXT NOT NULL,
    user_id INT NOT NULL,
    date_added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (entry_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- -----------------------------------
-- Information retrieval
-- -----------------------------------
DROP TABLE IF EXISTS unique_words;

CREATE TABLE unique_words (
    word_id INT NOT NULL AUTO_INCREMENT,
    word TINYTEXT NOT NULL,
    idf_values FLOAT, -- it can be null as it values need to be inserted, before calculating these.
    PRIMARY KEY (word_id)
);

SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
 -- Restore original checks and constraint settings --