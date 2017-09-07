drop table if exists guestbook;
create table guestbook (
  id integer primary key autoincrement,
  name text not null,
  'date' date not null,
  'text' text not null
);