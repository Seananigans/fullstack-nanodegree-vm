# Tournament Results
This repository uses postgresql to manage a Swiss tournament style tracking.

## Installation



## Usage

First create the database by starting up posgresql and executing the following command:
`CREATE DATABASE tournament;`

Set up the tables in the database by running the code in `tournament.sql`.

Then test the program using:
`python tournament_test.py`

The test program should verify that the below functions are working properly.

* deleteMatches()
	- Clear all scores from a tournament to restart the tournament with the same players.

* deletePlayers()
	- Clear the tournament to start with new players.

* registerPlayer(player_name)
	- Register a player in the tournament.

* countPlayers()
	- Count the number of players in the tournament.

* playerStandings()
	- Get the player standings.

* reportMatch(id_of_winner, id_of_loser)
	- Update the tournament results by reporting the winner and loser of a match.

* swissPairings()
	- Get the pairings for the next matches.