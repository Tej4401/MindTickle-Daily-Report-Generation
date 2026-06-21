-- CREATE TABLE for mindtickle_users
CREATE TABLE mindtickle_users (
    user_id serial PRIMARY KEY,
    user_name VARCHAR (255) NOT NULL,
    active_status VARCHAR (10) NOT NULL
);

-- INSERT Sample Data
INSERT INTO mindtickle_users (user_id, user_name, active_status) VALUES
    (1, 'Alice Smith', 'active'),
    (2, 'Bob Jones', 'active'),
    (3, 'Carmen Lee', 'inactive'),
    (4, 'Daniel Park', 'active'),
    (5, 'Emily Wu', 'active');
