INSERT INTO users (first_name, surname, username, password_hash) VALUES
("user", "5", "user5", "5d557544916fde5c6b162cfcbce84181fb2cbe8798439b643edf96ee4c5826b4");

INSERT INTO recommendations (user_id, book_id, certainty) VALUES
(1, 1, 0.5),
(1, 2, 0.5),
(2, 3, 0.5),
(2, 4, 0.5),
(3, 5, 0.5),
(3, 1, 0.5),
(4, 2, 0.5),
(4, 3, 0.5);