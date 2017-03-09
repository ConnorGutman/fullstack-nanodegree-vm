#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect(database_name="tournament"):
    # Connect to the PostgreSQL database.  Returns a database connection.
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        c = db.cursor()
        return db, c
    except:
        print("<error message>")


def deleteMatches():
    # Remove all the match records from the database.
    db, c = connect()
    # Delete all rows in matches and set matches+wins to 0 in players table
    c.execute("TRUNCATE matches;")
    c.execute("UPDATE players SET wins = 0")
    c.execute("UPDATE players SET matches = 0")
    db.commit()
    db.close()


def deletePlayers():
    # Remove all the player records from the database.
    db, c = connect()
    # Delete all rows in players and reset the sequence
    c.execute("TRUNCATE players CASCADE;")
    c.execute("ALTER SEQUENCE players_user_id_seq RESTART WITH 1;")
    db.commit()
    db.close()


def countPlayers():
    # Returns the number of players currently registered.
    db, c = connect()
    # Get the number of rows in players
    c.execute("SELECT COUNT(*) FROM players")
    totalPlayers = c.fetchone()
    totalPlayers = totalPlayers[0]
    db.commit()
    db.close()
    return totalPlayers


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
     """

    db, c = connect()
    query = "INSERT INTO players (name, wins, matches) VALUES (%s, %s, %s)"
    params = (name, 0, 0)
    c.execute(query, params)
    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    db, c = connect()
    c.execute("SELECT * FROM players;")
    names = c.fetchall()
    totalPlayers = countPlayers()
    c.execute("SELECT COUNT(*) FROM matches")
    totalMatches = c.fetchall()
    totalMatches = totalMatches[0][0]
    # Initialize the list of tuples
    standings = []
    # Check if there's any recorded matches
    if totalMatches > 0:
        for number in xrange(0, totalPlayers):
                ID = number + 1
                name = names[number][1]
                query = "SELECT COUNT(*) FROM matches WHERE winner = %s"
                params = (str(number + 1))
                c.execute(query, params)
                win_count = c.fetchall()
                win_count = int(win_count[0][0])
                query = "SELECT COUNT(*) FROM matches WHERE loser = %s"
                params = (str(number + 1))
                c.execute(query, params)
                lose_count = c.fetchall()
                lose_count = int(lose_count[0][0])
                match_count = win_count + lose_count
                standing = (ID, name, win_count, match_count)
                # Add player tuple to list
                standings.append(standing)
    else:
        for number in xrange(0, totalPlayers):
                ID = names[number][0]
                name = names[number][1]
                win_count = 0
                match_count = 0
                standing = (ID, name, win_count, match_count)
                # Add player tuple to list
                standings.append(standing)
    db.commit()
    db.close()
    standings.sort(key=lambda tup: tup[2])
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db, c = connect()

    # Add a new match in matches table
    query = "INSERT INTO matches (winner, loser) VALUES (%s, %s)"
    params = (winner, loser)
    c.execute(query, params)
    db.commit()
    db.close()


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

    # Get all players and count them
    allPlayers = playerStandings()
    totalPlayers = len(allPlayers)
    # Initialize the list of tuples
    pairs = []
    # Example: 8 players would have 4 pairs
    for number in xrange(0, totalPlayers, 2):
            # Create tuple with ID1, Name1, ID2, Name2
            pair = (allPlayers[number][0], allPlayers[number][1],
                    allPlayers[number+1][0], allPlayers[number+1][1])
            # Add pair tuple to list
            pairs.append(pair)
    return pairs
