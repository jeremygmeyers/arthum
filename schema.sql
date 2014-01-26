drop table if exists images;
create table images (
  id integer primary key autoincrement,
  link text not null,
  artist text not null,
  title text not null,
  year integer not null
);

drop table if exists answers;
create table answers (
  id integer primary key autoincrement,
  imageID integer not null,
  title text not null,
  artist text not null,
  year integer not null,
  description integer not null,
  timestamp datetime
);
