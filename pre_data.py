"""A python script to insert pre-made data into the database."""

import sqlite3
from werkzeug.security import generate_password_hash

import config

# This is a python script that inserts custom data into database.db for testing.
# the script doesn't include images for users or games
# database.db and the tables in it have to exist before running the script
    # if database.db doesn't exist:
        # $ sqlite3 database.db < schema.sql
        # $ sqlite3 database.db < init.sql

TIME = config.TIME

db = sqlite3.connect("database.db")

db.execute("DELETE FROM Users")
db.execute("DELETE FROM Games")
db.execute("DELETE FROM Reviews")
db.execute("DELETE FROM Game_classes")
db.execute("DELETE FROM Images")

# all strings are str and values are int
# username, password, user id
users = [["RampageGames", "rampagegames", 1],
         ["Ibuhard", "ibuhard", 1],
         ["QubeSoftware", "qubesoftware", 1],
         ["SleeplessnessGames", "sleeplessnessgames", 1],
         ["Jason", "jason", 0],
         ["Emily", "emily", 0],
         ["Bob", "bob", 0],
         ["Chris", "chris", 0]]

# title, description, publisher id
games = [["Falorant", """Falorant is a team-based first-person tactical hero shooter set in the
          near future. Players play as one of a set of Agents, characters based on several
          countries and cultures around the world. In the main game mode, players are assigned
          to either the attacking or defending team with each team having five players
          on it.""", 1],
         ["The Squad", """Get ready to race across a massive, open-world recreation of
          the United States in The Squad! This isn't your average racing game; it's an
          action-packed adventure where you'll infiltrate criminal organizations, customize
          your dream car, and team up with friends to conquer the streets. Explore diverse
          locations, from bustling cityscapes to scenic landscapes, and experience the thrill
          of high-speed chases and daring missions.""", 2],
         ["Industrio", """Step right up and prepare to be amazed by Industrio, the ultimate
          factory-building game where you transform a desolate planet into a sprawling
          industrial empire! Industrio puts you in the shoes of an engineer stranded on an
          alien world, tasked with harvesting resources, crafting machines, and ultimately
          launching a rocket to escape.""", 3],
         ["Sprocket and Rattle: A Fracture in Time", """Sprocket and Rattle: A Fracture in Time
          is a sci-fi action-adventure game where players control Sprocket, a Xabmol mechanic,
          and his robot friend Rattle as they fight to stop the nefarious Dr. Villainous from
          rewriting history. Separated at the start, Sprocket explores the galaxy searching for
          Rattle, while Rattle discovers his mysterious connection to time itself and gains new
          time-manipulation abilities. The game blends fast-paced combat, creative puzzles, and
          space exploration with an emotional story about friendship, destiny, and the power
          of choice.""", 4],
         ["Bob Fancy's Colorful 6 Assault", """Bob Fancy's Colorful 6 Assault is a tactical 5v5
          shooter focused on strategy, precision, and intense close-quarters combat. Players
          choose unique Operators with specialized gadgets to breach or defend fortified positions.
          With destructible environments, drones, and surveillance tools, every match demands
          communication, quick thinking, and smart team play.""", 2]]

# content, user id, game id, score
reviews = [["Similar to CDMCA 2 but with abilities.", 5, 1, 3],
           ["My favorite game when I first got a proper PC :)", 8, 1, 5],
           ["wayyyyyyy better than CDMCA 2", 6, 1, 5],
           ["Crazy how you can explore the ENTIRE US!", 5, 2, 5],
           ["Apparently Ibuhard is taking the game offline...", 6, 2, 1],
           ["My most played racing game", 8, 2, 5],
           ["bob :)", 7, 2, 5],
           ["This game is way better than the 3D copycat version.", 6, 3, 4],
           ["INSANELY addictive!", 8, 3, 5],
           ["The puzzles are too hard :/", 5, 4, 2],
           ["I love how unique the different planets are", 6, 4, 5],
           ["My childhood!!!", 8, 4, 5],
           ["THEY NAMED A GAME AFTER ME!!!", 7, 5, 5],
           ["My most played game by far", 8, 5, 5]]

# game id, class, value
classes = [[1, "Category", "Action"],
           [1, "Category", "Competitive"],
           [1, "Category", "Multiplayer"],
           [1, "Category", "Strategy"],
           [2, "Category", "Multiplayer"],
           [2, "Category", "Racing"],
           [2, "Category", "Sandbox"],
           [3, "Category", "Management"],
           [3, "Category", "Strategy"],
           [3, "Category", "Survival"],
           [4, "Category", "Action"],
           [4, "Category", "Adventure"],
           [4, "Category", "Platformer"],
           [5, "Category", "Action"],
           [5, "Category", "Competitive"],
           [5, "Category", "Multiplayer"],
           [5, "Category", "Strategy"]]

for username, password, developer in users: # inserts the users
    password_hash = generate_password_hash(password)
    sql = """INSERT INTO Users (username, password_hash, developer)
             VALUES (?, ?, ?)"""
    db.execute(sql, [username, password_hash, developer])

for title, description, user_id in games: # inserts the games
    sql = f"""INSERT INTO Games (title, description, uploaded_at, user_id)
              VALUES (?, ?, datetime('now', '{TIME}'), ?)"""
    db.execute(sql, [title, description, user_id])

for content, user_id, game_id, score in reviews: # inserts the reviews
    sql = f"""INSERT INTO Reviews (content, sent_at, user_id, game_id, score)
              VALUES (?, datetime('now', '{TIME}'), ?, ?, ?)"""
    db.execute(sql, [content, user_id, game_id, score])

for game_id, title, value in classes: # inserts the categories for games
    sql = """INSERT INTO Game_classes (game_id, title, value)
             VALUES (?, ?, ?)"""
    db.execute(sql, [game_id, title, value])

db.commit()
db.close()
