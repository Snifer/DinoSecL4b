CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

INSERT INTO users (username, password) VALUES ('snifer', '1234');
INSERT INTO users (username, password) VALUES ('rizeltane', '123');
INSERT INTO users (username, password) VALUES ('dev','dev');

CREATE TABLE guestbook (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME NOT NULL
);

