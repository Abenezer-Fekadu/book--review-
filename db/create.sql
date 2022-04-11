DROP TABLE IF EXISTS "users";
CREATE TABLE users (
    uid serial PRIMARY KEY,
    username VARCHAR(100) not null unique,
    email VARCHAR(120) not null unique,
    pwdhash VARCHAR(200) not null
);

CREATE TABLE books (
    bid SERIAL PRIMARY KEY,
    isbn VARCHAR(20) not null unique,
    title VARCHAR(100) not null,
    author VARCHAR(100) not null,
    year VARCHAR(10) not null,
);

DROP TABLE IF EXISTS "reviews";
CREATE TABLE reviews (
    rid SERIAL PRIMARY KEY,
    rate INTEGER NOT NULL,
    review VARCHAR NOT NULL, 
    book_id VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    CONSTRAINT "book_id_fkey" FOREIGN KEY (book_id) REFERENCES books(isbn) ON DELETE CASCADE NOT DEFERRABLE,
    CONSTRAINT "user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE NOT DEFERRABLE
);