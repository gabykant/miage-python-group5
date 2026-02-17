-- ============================================================
-- schema.sql — Création de la base de données
-- mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS python_miage
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE python_miage;

-- ── Table users ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id          INT(20) AUTO_INCREMENT PRIMARY KEY,
    firstname   VARCHAR(191)  NOT NULL,
    lastname    VARCHAR(191)  NOT NULL,
    email       VARCHAR(191)  NOT NULL UNIQUE,
    password    VARCHAR(191)  NOT NULL,
    role        ENUM('admin', 'student', 'bookkeeper') NOT NULL DEFAULT 'student',
    matricule            VARCHAR(20),
    field_study          VARCHAR(100) NULL,
    phone_number         VARCHAR(20) NULL,
    speciality           VARCHAR(100) NULL,
    level                VARCHAR(20) NULL,
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- ── Table books ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS books (
    id          INT(20) AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(191)  NOT NULL,
    author      VARCHAR(191)  NOT NULL,
    isbn        VARCHAR(20)   NOT NULL UNIQUE,
    publised_year        YEAR,
    publisher       VARCHAR(100),
    copies INT NOT NULL DEFAULT 1,
    available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    -- ADD CONSTRAINT chk_copies CHECK (copies >= 0),
    -- ADD CONSTRAINT chk_available CHECK (available IN (0, 1)),
    -- ADD INDEX ux_books_isbn (isbn)
);

-- ── Table emprunts ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS borrows (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    book_id             INT  NOT NULL,
    user_id             INT  NOT NULL,
    borrowed_at         DATE NOT NULL DEFAULT (CURDATE),
    due_date  DATE NOT NULL,
    returned_at         DATE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (book_id)    REFERENCES books(id)    ON DELETE RESTRICT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
);

-- ── Données de test ───────────────────────────────────────────
INSERT INTO users (firstname, lastname, email, password, role, matricule, field_study, level) VALUES
    ('Gabriel', 'Kwaye', 'gabrielkwaye@gmail.com', '$2b$12$yfvHH84O8Jz3yE8rupfauOwM58SsTNqRXXVlaRQv7ZMZUwyNRkzqm', 'admin', null, null, null);

INSERT INTO books (title, author, isbn, publised_year, publisher, copies) VALUES
    ('Introduction aux algorithmes',  'Cormen et al.',    '978-0-262-03384-8', 2009, 'MIT Press', 13),
    ('Python Fluent',                 'Luciano Ramalho',  '978-1-491-94600-8', 2022, 'O\"Reilly Media', 7),
    ('Analyse mathématique',          'Walter Rudin',     '978-0-070-54235-8', 1976, 'McGraw-Hill', 6),
    ('Le Code da Vinci',              'Dan Brown',        '978-2-709-62568-5', 2004, 'L\"Harmattan',   5);