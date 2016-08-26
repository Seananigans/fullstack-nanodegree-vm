-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE IF NOT EXISTS players (
	id SERIAL PRIMARY KEY,
	name TEXT);

CREATE TABLE IF NOT EXISTS matches (
	id SERIAL PRIMARY KEY,
	winner INTEGER REFERENCES players (id),
	loser INTEGER REFERENCES players (id));

CREATE VIEW wins AS 
	SELECT players.id, COUNT(matches.winner) as ws
	FROM players 
	LEFT JOIN matches 
	ON players.id=matches.winner 
	GROUP BY players.id;

CREATE VIEW total AS 
	SELECT players.id, COUNT(matches.winner) as tot
	FROM players 
	LEFT JOIN matches 
	ON players.id=matches.winner OR players.id=matches.loser
	GROUP BY players.id;

CREATE VIEW standings AS
	SELECT players.id, players.name, wins.ws as wins, total.tot as matches
	FROM players, wins, total
	WHERE players.id = wins.id and players.id = total.id
	ORDER BY wins DESC;