-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;
CREATE TABLE players ( user_id serial PRIMARY KEY, name VARCHAR (50) NOT NULL);
CREATE TABLE matches ( winner integer references players(user_id), loser integer references players(user_id));
