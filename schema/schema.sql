drop table if exists entries;
create table entries (
        id integer primary key autoincrement,
        title text not null,
        text text not null,
        required char(1) NOT NULL,
        category char(20) NOT NULL
        );

drop table if exists users;
create table users (
        id integer primary key autoincrement,
        username text not null,
        password text not null
        );
DROP TABLE IF EXISTS required;
CREATE TABLE required (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  text TEXT NOT NULL,
  required char(1) NOT NULL,
  category char(20) NOT NULL
);
