DROP TABLE IF EXISTS lesson_completion;

CREATE TABLE lesson_completion (
    completion_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    lesson_id INT NOT NULL,
    completion_date DATE NOT NULL
);

INSERT INTO lesson_completion (
    user_id,
    lesson_id,
    completion_date
) VALUES

-- Alice: multiple lessons on one day
(1, 101, '2026-06-18'),
(1, 102, '2026-06-18'),
(1, 103, '2026-06-18'),

-- Alice: repeat lesson on another day
(1, 101, '2026-06-19'),
(1, 104, '2026-06-19'),

-- Bob: multiple lessons and a duplicate record
(2, 201, '2026-06-18'),
(2, 202, '2026-06-19'),
(2, 202, '2026-06-19'),
(2, 203, '2026-06-19'),

-- Carmen: inactive user data should be ignored
(3, 301, '2026-06-18'),
(3, 302, '2026-06-19'),

-- Daniel: single daily report entries
(4, 401, '2026-06-18'),
(4, 402, '2026-06-19'),
(4, 403, '2026-06-20'),

-- Emily: high volume on one day
(5, 501, '2026-06-19'),
(5, 502, '2026-06-19'),
(5, 503, '2026-06-19'),
(5, 504, '2026-06-19'),
(5, 505, '2026-06-19');
