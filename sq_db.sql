CREATE TABLE IF NOT EXISTS mainmenu(
id int NOT NULL,
title text NOT NULL,
url text NOT NULL,
PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS posts (
id int NOT NULL,
title text NOT NULL,
text text NOT NULL,
url text NOT NULL,
time integer NOT NULL,
PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS users (
id integer,
name text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
avatar BLOB DEFAULT NULL,
time integer NOT NULL,
PRIMARY KEY(id AUTOINCREMENT)
);