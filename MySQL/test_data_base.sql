INSERT INTO authors (first_name, surname, about, clean_name) VALUES
("Author", "1", "This is the first author's about.", "author 1"),
("Author", "2", "This is the second author's about.", "author 2"),
("Author", "3", "This is the third author's about.", "author 3");

INSERT INTO genres (name, about, clean_name) VALUES
("Genre 1", "This genre does not have an about", "genre 1"),
("Genre 2", "This genre does not have an about", "genre 2"),
("Genre 3", "This genre does not have an about", "genre 3"),
("Genre 4", "This genre does not have an about", "genre 4"),
("Genre 5", "This genre does not have an about", "genre 5"),
("Genre 6", "This genre does not have an about", "genre 6"),
("Genre 7", "This genre does not have an about", "genre 7"),
("Genre 8", "This genre does not have an about", "genre 8"),
("Genre 9", "This genre does not have an about", "genre 9"),
("Genre 10", "This genre does not have an about", "genre 10");

INSERT INTO users (first_name, surname, username, password_hash, preferences_set) VALUES
("user", "1", "user1", "5d557544916fde5c6b162cfcbce84181fb2cbe8798439b643edf96ee4c5826b4", TRUE),
("user", "2", "user2", "5d557544916fde5c6b162cfcbce84181fb2cbe8798439b643edf96ee4c5826b4", TRUE),
("user", "3", "user3", "5d557544916fde5c6b162cfcbce84181fb2cbe8798439b643edf96ee4c5826b4", TRUE),
("user", "4", "user4", "5d557544916fde5c6b162cfcbce84181fb2cbe8798439b643edf96ee4c5826b4", TRUE);

INSERT INTO books (author_id, title, clean_title, synopsis, cover_image, purchase_link, fiction, release_date, isbn) VALUES
(1, "Book 1", "book 1", "This book does not have a synopsis", "", "", 1, "2022-2-2", "0111111111"),
(2, "Book 2", "book 2", "This book does not have a synopsis", "", "", 1, "2022-2-2", "0222222222"),
(3, "Book 3", "book 3", "This book does not have a synopsis", "", "", 1, "2022-2-2", "0333333333"),
(2, "Book 4", "book 4", "This book does not have a synopsis", "", "", 1, "2022-2-2", "0444444444"),
(1, "Book 5", "book 5", "This book does not have a synopsis", "", "", 1, "2022-2-2", "0555555555");

INSERT into reviews (book_id, user_id, overall_rating, plot_rating, character_rating) VALUES
(1, 1, 5, 5, 5),
(1, 3, 2, 3, 1),
(2, 1, 3, 2, 3),
(2, 2, 5, 2, 5),
(2, 4, 4, 3, 4),
(3, 2, 5, 3, 4),
(3, 3, 1, 1, 2),
(3, 4, 3, 2, 4),
(4, 1, 3, 2, 5),
(4, 2, 3, 3, 4),
(4, 3, 1, 2, 3),
(4, 4, 4, 3, 5),
(5, 1, 1, 2, 1);

-- book 1 avg: 3.5
-- book 2 avg: 4
-- book 3 avg: 3
-- book 4 avg: 2.75
-- book 5 avg: 1


INSERT INTO book_genres (book_id, genre_id, match_strength) VALUES
(1, 1, 0.09616839),
(1, 2, 0.13990453),
(1, 3, -0.19446672),
(1, 4, 0.52190524),
(1, 5, 0.27685214),
(1, 6, -0.47304706),
(1, 7, 0.35159769),
(1, 8, 0.7532494),
(1, 9, 0.68760675),
(1, 10, -0.17612252),
(2, 1, -0.11439516),
(2, 2, 0.4602393),
(2, 3, 0.31336525),
(2, 4, 0.00427231),
(2, 5, 0.03817313),
(2, 6, -0.01841387),
(2, 7, -0.0327723),
(2, 8, 0.30054946),
(2, 9, -0.05232584),
(2, 10, 0.26632295),
(3, 1, -0.34141417),
(3, 2, 0.74010668),
(3, 3, 0.874315),
(3, 4, 1.24445128),
(3, 5, -0.32515329),
(3, 6, 0.63977702),
(3, 7, -0.61130751),
(3, 8, -0.13086895),
(3, 9, 0.18113549),
(3, 10, 0.58969151),
(4, 1, 0.89826349),
(4, 2, 1.67033071),
(4, 3, 0.34160336),
(4, 4, -0.55935626),
(4, 5, 0.68218074),
(4, 6, -0.15577632),
(4, 7, -0.26834166),
(4, 8, -0.33200523),
(4, 9, 0.15145078),
(4, 10, 0.37327423),
(5, 1, 0.83968715),
(5, 2, 0.3026473),
(5, 3, -0.21344638),
(5, 4, 1.1563066),
(5, 5, 0.22312092),
(5, 6, 0.2789436),
(5, 7, -0.45117512),
(5, 8, -1.04237929),
(5, 9, 0.95588463),
(5, 10, -0.27979377);

INSERT INTO sessions (client_id, user_id) VALUES
("asdhjaksnce1263872613", 1),
("adqweqiueqw0812309812", 1),
("zxmcabvzxcn1231231235", 1),
("poipoqwerwrw983453453", 3),
("swcdecwftrbr132788943", 3);

INSERT INTO sessions (client_id, user_id, date_added) VALUES
("swcdeawftrbr132788943", 2, "2021-2-2"),
("sdfasdvnjtit987652678", 1, "2020-3-4"),
("lmoijbnernub125392872", 4, "2022-12-8");

INSERT INTO reading_list_names (list_name, user_id) VALUES
("Want to Read", 1),
("Currently Reading", 1),
("Have Read", 1),
("Want to Read", 2),
("Currently Reading", 2),
("Have Read", 2),
("Want to Read", 3),
("Currently Reading", 3),
("Have Read", 3),
("Want to Read", 4),
("Currently Reading", 4),
("Have Read", 4);

INSERT INTO author_followers (user_id, author_id) VALUES
(1, 1),
(1, 2),
(2, 1),
(2, 2),
(3, 2);

INSERT INTO diary_entries (user_id, book_id, overall_rating, character_rating, plot_rating, summary, thoughts, pages_read) VALUES
(1, 1, 5, 3, 2, "Summary", "Thoughts", 10),
(1, 1, 1, 2, 5, "Entry summary", "Entry thoughts", 21),
(1, 2, 5, 3, 2, "A summary", "Thoughts", 11),
(2, 5, 2, 4, 1, "Entry summary", "Entry thoughts", 2),
(2, 4, 4, 5, 3, "Short entry summary", "Long entry thoughts.", 5);

INSERT INTO reading_lists (user_id, list_id, book_id) VALUES
(1, 3, 1),
(1, 3, 2),
(1, 3, 4),
(1, 3, 5),
(2, 6, 2),
(2, 6, 3),
(2, 6, 4),
(3, 9, 1),
(3, 9, 3),
(3, 9, 4),
(4, 12, 2),
(4, 12, 3),
(4, 12, 4);

INSERT INTO bad_recommendations (user_id, book_id) VALUES
(1, 3),
(1, 5),
(2, 1);
