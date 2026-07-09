-- SQLite
-- add columns
alter table messages add column server_id integer;
alter table users add column server_id integer;


-- make it so the existing messages and users are for better columbia
-- write in the real id over 9999, I left it out of git 
update messages set server_id = 9999 where server_id is null;
update users set server_id = 9999 where server_id is null;

-- manually set a server id
update messages set server_id = 0 where id = 32;