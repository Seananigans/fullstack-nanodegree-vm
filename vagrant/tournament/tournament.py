#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from pprint import pprint

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        return psycopg2.connect("dbname=tournament")
    except Exception as e:
        print "Connection failed with exception:", str(e)


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()

    query = "UPDATE tournament SET matches=0, wins=0;"
    c.execute(query)
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()

    query = "DELETE FROM tournament;"
    c.execute(query)
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()

    query = "SELECT COUNT(*) FROM tournament;"
    c.execute(query)
    count = c.fetchone()[0]
    DB.close()
    return count


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    query = "INSERT INTO tournament (player, wins, matches) VALUES (%s, %s, %s)"
    c.execute(query, (name, 0, 0))
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()

    query = "SELECT * FROM tournament ORDER BY wins DESC;"
    c.execute(query)
    standings = [row for row in c.fetchall()]
    DB.close()
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()

    # Winner Update
    query = "SELECT wins, matches FROM tournament WHERE id=%s;" 
    c.execute(query, (winner,))
    wins, matches = c.fetchone()
    query = "UPDATE tournament SET wins=%s, matches=%s WHERE id=%s;"
    c.execute(query, (wins+1, matches+1, winner))
    DB.commit()

    #Loser Update
    query = "SELECT matches FROM tournament WHERE id=%s;"
    c.execute(query, (loser,))
    matches = c.fetchone()[0]
    query = "UPDATE tournament SET matches=%s WHERE id=%s;"
    c.execute(query, (matches+1, loser))
    DB.commit()

    DB.close()
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # DB = connect()
    # c = DB.cursor()

    # Retrieve player standings
    standings = playerStandings()
    # Create Matches by popping the first two players off the top of the list and
    # adding them to a matches list.
    matches = []
    while len(standings) > 1:
        # Creat match tuple
        item = []
        for i in standings[:2]:
            item.append(i[0])
            item.append(i[1])
        # Add match to the matches list
        matches.append(tuple(item))
        # Remove top two players from original sorted list
        standings = standings[2:]
    return matches


