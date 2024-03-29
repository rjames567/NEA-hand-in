INSERT INTO authors (first_name, surname, about, clean_name) VALUES
('Kristin', 'Hannah', 'This author does not have an about', 'kristin hannah'),
('B.A.', 'Paris', 'This author does not have an about', 'ba paris'),
('George', 'Orwell', ' This author does not have an about', 'george orwell'),
('Mary', 'E. Pearson', 'This author does not have an about', 'mary e pearson'),
('Kurt', 'Vonnegut Jr.', 'This author does not have an about', 'kurt vonnegut jr'),
('Rick', 'Riordan', 'This author does not have an about', 'rick riordan'),
('Madeleine', "L'Engle", 'This author does not have an about', 'madeleine lengle'),
('Alyson', 'Noel', 'This author does not have an about', 'alyson noel'),
('Jay', 'Asher', 'This author does not have an about', 'jay asher'),
('Marie', 'Kondo', 'This author does not have an about', 'marie kondo'),
('William', 'Goldman', 'This author does not have an about', 'william goldman'),
('Barbara', 'Kingsolver', 'This author does not have an about', 'barbara kingsolver'),
('Susan', 'Ee', 'This author does not have an about', 'susan ee'),
('Gregory', 'Maguire', 'This author does not have an about', 'gregory maguire'),
('Bill', 'Bryson', 'This author does not have an about', 'bill bryson'),
('Jennifer', 'L. Armentrout', 'This author does not have an about', 'jennifer l armentrout'),
('Kristin', 'Cashore', 'This author does not have an about', 'kristin cashore'),
('Aziz', 'Ansari', 'This author does not have an about', 'aziz ansari'),
('Abbi', 'Glines', 'This author does not have an about', 'abbi glines');

INSERT INTO books (author_id, title, clean_title, synopsis, cover_image, purchase_link, fiction, release_date, isbn) VALUES
(4, "The Nightingale", "the nightingale", "", "", "", 1, "2015-01-01", "41125521"),
(3, "Animal Farm", "animal farm", "", "", "", 1, "2003-01-01", "2207778"),
(7, "The Kiss of Deception (The Remnant Chronicles, #1)", "the kiss of deception the remnant chronicles 1", "", "", "", 1, "2014-01-01", "22617247"),
(9, "The Sea of Monsters (Percy Jackson and the Olympians, #2)", "the sea of monsters percy jackson and the olympians 2", "", "", "", 1, "2006-01-01", "43554"),
(9, "The Son of Neptune (The Heroes of Olympus, #2)", "the son of neptune the heroes of olympus 2", "", "", "", 1, "2011-01-01", "14406312"),
(9, "The Last Olympian (Percy Jackson and the Olympians, #5)", "the last olympian percy jackson and the olympians 5", "", "", "", 1, "2009-01-01", "4551489"),
(9, "The Sword of Summer (Magnus Chase and the Gods of Asgard, #1)", "the sword of summer magnus chase and the gods of asgard 1", "", "", "", 1, "2015-01-01", "21400019"),
(9, "The Red Pyramid (Kane Chronicles, #1)", "the red pyramid kane chronicles 1", "", "", "", 1, "2010-01-01", "346572"),
(11, "Evermore (The Immortals, #1)", "evermore the immortals 1", "", "", "", 1, "1990-01-01", "4021549"),
(13, "The Life-Changing Magic of Tidying Up: The Japanese Art of Decluttering and Organizing", "the lifechanging magic of tidying up the japanese art of decluttering and organizing", "", "", "", 1, "2014-01-01", "41711738"),
(15, "The Poisonwood Bible", "he poisonwood bible", "", "", "", 1, "2005-01-01", "810663"),
(16, "Angelfall (Penryn & the End of Days, #1)", "angelfall penryn  the end of days 1", "", "", "", 1, "2013-01-01", "16435765"),
(18, "A Walk in the Woods", "a walk in the woods", "", "", "", 1, "1990-01-01", "613469"),
(19, "Onyx (Lux, #2)", "onyx lux 2", "", "", "", 1, "2012-01-01", "18211575"),
(19, "Opal (Lux, #3)", "opal lux 3", "", "", "", 1, "2012-01-01", "18591132"),
(19, "Origin (Lux, #4)", "origin lux 4", "", "", "", 1, "2013-01-01", "19259997"),
(20, "Graceling (Graceling Realm, #1)", "graceling graceling realm 1", "", "", "", 1, "2008-01-01", "3270810"),
(21, "Modern Romance", "modern romance", "", "", "", 1, "2015-01-01", "43014915");

INSERT INTO book_genres (book_id, genre_id, match_strength) VALUES
(6, 1, 0.73),
(6, 2, 0.5),
(6, 3, 0.13),
(6, 4, 0.0),
(6, 5, 0.9),
(6, 6, 0.51),
(6, 7, 0.32),
(6, 8, 0.07),
(6, 9, 0.37),
(6, 10, 0.3),
(7, 1, 0.56),
(7, 2, 0.76),
(7, 3, 0.88),
(7, 4, 0.32),
(7, 5, 0.88),
(7, 6, 0.72),
(7, 7, 0.5),
(7, 8, 0.15),
(7, 9, 0.71),
(7, 10, 0.99),
(8, 1, 0.96),
(8, 2, 0.8),
(8, 3, 0.67),
(8, 4, 0.82),
(8, 5, 0.71),
(8, 6, 0.37),
(8, 7, 0.05),
(8, 8, 0.38),
(8, 9, 0.01),
(8, 10, 0.64),
(9, 1, 0.02),
(9, 2, 0.67),
(9, 3, 0.11),
(9, 4, 0.12),
(9, 5, 0.36),
(9, 6, 0.57),
(9, 7, 0.69),
(9, 8, 0.17),
(9, 9, 0.3),
(9, 10, 0.9),
(10, 1, 0.3),
(10, 2, 0.03),
(10, 3, 0.88),
(10, 4, 0.91),
(10, 5, 0.74),
(10, 6, 0.62),
(10, 7, 0.36),
(10, 8, 0.13),
(10, 9, 0.17),
(10, 10, 0.18),
(11, 1, 0.34),
(11, 2, 0.72),
(11, 3, 0.12),
(11, 4, 0.54),
(11, 5, 0.98),
(11, 6, 0.49),
(11, 7, 0.32),
(11, 8, 0.34),
(11, 9, 0.83),
(11, 10, 0.8),
(12, 1, 0.48),
(12, 2, 0.31),
(12, 3, 0.71),
(12, 4, 0.28),
(12, 5, 0.86),
(12, 6, 0.4),
(12, 7, 0.65),
(12, 8, 0.62),
(12, 9, 0.95),
(12, 10, 0.05),
(13, 1, 0.26),
(13, 2, 1.0),
(13, 3, 0.88),
(13, 4, 0.58),
(13, 5, 0.79),
(13, 6, 0.23),
(13, 7, 0.93),
(13, 8, 0.59),
(13, 9, 0.54),
(13, 10, 0.91),
(14, 1, 0.83),
(14, 2, 0.59),
(14, 3, 0.2),
(14, 4, 0.81),
(14, 5, 0.72),
(14, 6, 0.99),
(14, 7, 0.18),
(14, 8, 0.11),
(14, 9, 0.32),
(14, 10, 0.92),
(15, 1, 0.89),
(15, 2, 0.0),
(15, 3, 0.75),
(15, 4, 0.81),
(15, 5, 0.91),
(15, 6, 0.67),
(15, 7, 0.48),
(15, 8, 0.0),
(15, 9, 0.29),
(15, 10, 0.52),
(16, 1, 0.43),
(16, 2, 0.32),
(16, 3, 0.82),
(16, 4, 0.76),
(16, 5, 0.85),
(16, 6, 0.34),
(16, 7, 0.34),
(16, 8, 0.54),
(16, 9, 0.51),
(16, 10, 0.74),
(17, 1, 0.07),
(17, 2, 0.55),
(17, 3, 0.51),
(17, 4, 0.44),
(17, 5, 0.21),
(17, 6, 0.73),
(17, 7, 0.44),
(17, 8, 0.21),
(17, 9, 0.5),
(17, 10, 0.84),
(18, 1, 0.63),
(18, 2, 0.94),
(18, 3, 0.6),
(18, 4, 0.65),
(18, 5, 0.57),
(18, 6, 0.51),
(18, 7, 0.81),
(18, 8, 0.72),
(18, 9, 0.55),
(18, 10, 0.76),
(19, 1, 0.15),
(19, 2, 0.33),
(19, 3, 0.3),
(19, 4, 0.25),
(19, 5, 0.94),
(19, 6, 0.66),
(19, 7, 0.46),
(19, 8, 0.63),
(19, 9, 0.67),
(19, 10, 0.33),
(20, 1, 0.19),
(20, 2, 0.53),
(20, 3, 0.26),
(20, 4, 0.92),
(20, 5, 0.24),
(20, 6, 0.56),
(20, 7, 0.17),
(20, 8, 0.65),
(20, 9, 0.65),
(20, 10, 0.19),
(21, 1, 0.01),
(21, 2, 0.33),
(21, 3, 0.7),
(21, 4, 0.42),
(21, 5, 0.72),
(21, 6, 0.49),
(21, 7, 0.54),
(21, 8, 0.92),
(21, 9, 0.67),
(21, 10, 0.12),
(22, 1, 0.39),
(22, 2, 0.23),
(22, 3, 0.38),
(22, 4, 0.45),
(22, 5, 0.96),
(22, 6, 0.04),
(22, 7, 0.75),
(22, 8, 0.72),
(22, 9, 0.14),
(22, 10, 0.7),
(23, 1, 0.27),
(23, 2, 0.48),
(23, 3, 0.26),
(23, 4, 0.48),
(23, 5, 0.17),
(23, 6, 0.63),
(23, 7, 0.29),
(23, 8, 0.47),
(23, 9, 0.94),
(23, 10, 0.49);


INSERT INTO users (first_name, surname, username, password_hash) VALUES
("user", "5", "user5", "5d557544916fde5c6b162cfcbce84181fb2cbe8798439b643edf96ee4c5826b4");

INSERT INTO reading_lists (user_id, list_id, book_id) VALUES -- users 1,2,3,4
(1, 1, 6),
(1, 1, 9),
(1, 2, 13),
(2, 4, 13),
(2, 4, 7),
(2, 4, 15),
(2, 5, 16),
(2, 5, 1),
(3, 7, 7),
(3, 7, 8),
(3, 8, 2),
(3, 8, 20),
(3, 8, 5),
(4, 10, 11),
(4, 10, 13),
(4, 10, 15),
(4, 10, 1),
(4, 11, 5);

INSERT INTO reading_list_names (list_name, user_id) VALUES
("Test list", 1),
("Test list", 2),
("Want to Read", 5),
("Currently Reading", 5),
("Have Read", 5);

INSERT INTO reading_lists (user_id, list_id, book_id) VALUES
(1, 13, 21)