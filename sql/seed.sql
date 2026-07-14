-- Dummy schema and data for local testing against the Oracle Free container.

DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;

CREATE TABLE authors (
    id      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name    VARCHAR2(100) NOT NULL,
    country VARCHAR2(100)
);

CREATE TABLE books (
    id             NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title          VARCHAR2(200) NOT NULL,
    author_id      NUMBER NOT NULL REFERENCES authors(id),
    published_year NUMBER(4)
);

INSERT INTO authors (name, country) VALUES ('Ursula K. Le Guin', 'USA');
INSERT INTO authors (name, country) VALUES ('Isaac Asimov', 'USA');
INSERT INTO authors (name, country) VALUES ('Liu Cixin', 'China');
INSERT INTO authors (name, country) VALUES ('Ann Leckie', 'USA');

INSERT INTO books (title, author_id, published_year) VALUES ('The Left Hand of Darkness', 1, 1969);
INSERT INTO books (title, author_id, published_year) VALUES ('The Dispossessed', 1, 1974);
INSERT INTO books (title, author_id, published_year) VALUES ('Foundation', 2, 1951);
INSERT INTO books (title, author_id, published_year) VALUES ('I, Robot', 2, 1950);
INSERT INTO books (title, author_id, published_year) VALUES ('The Three-Body Problem', 3, 2008);
INSERT INTO books (title, author_id, published_year) VALUES ('Ancillary Justice', 4, 2013);

COMMIT;

EXIT;
