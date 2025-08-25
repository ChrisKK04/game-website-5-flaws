"""A python script to insert a large dataset into the database."""

import random
import sqlite3

# the script doesn't include images for users or games
# database.db and the tables in it have to exist before running the script
    # if database.db doesn't exist:
        # $ database.db < schema.sql
# logging in to the generated users isn't possible
    # (because the passwords aren't saved as hashes and the app checks for hashes)
        # (generating the hashes takes too long for testing)
# running the script takes about 10 seconds

db = sqlite3.connect("database.db")

db.execute("DELETE FROM Users")
db.execute("DELETE FROM Games")
db.execute("DELETE FROM Reviews")
db.execute("DELETE FROM Game_classes")
db.execute("DELETE FROM Images")

USER_COUNT = 1000 # 1/2 developers 1/2 reviews (1 - 500 developers 501 - 1000 reviewers)
GAME_COUNT = 10**5
REVIEW_CONTENT = 10**6
GAME_CLASSES = 10**5 # amount of classes added to games
CLASSES = ['Category'] # classes
CATEGORY_CLASSES = ['racing', 'simulator', 'roguelike', 'action', 'RPG']
# class -> category -> values

for i in range(1, USER_COUNT + 1): # insert users
    developer = 1 if i < 501 else 0
    db.execute("""INSERT INTO Users (username, password_hash, developer)
                  VALUES (?, ?, ?)""",
                ["user" + str(i), "user" + str(i), developer])

for i in range(1, GAME_COUNT + 1): # insert games
    user_id = random.randint(1, USER_COUNT // 2)
    db.execute("""INSERT INTO Games (title, description, uploaded_at, user_id)
                  VALUES (?, ?, datetime('now'), ?)""",
               ["game" + str(i), "game" + str(i), user_id])

for i in range(1, REVIEW_CONTENT + 1): # insert reviews
    user_id = random.randint(501, USER_COUNT)
    game_id = random.randint(1, GAME_COUNT)
    score = random.choice([1, 2, 3, 4, 5])
    db.execute("""INSERT INTO Reviews (content, sent_at, user_id, game_id, score)
                  VALUES (?, datetime('now'), ?, ?, ?)""",
                ["message" + str(i), user_id, game_id, score])

for i in range(1, GAME_CLASSES + 1):
    game_id = random.randint(1, GAME_COUNT)
    title = random.choice(CLASSES)
    value = random.choice(CATEGORY_CLASSES)
    db.execute("""INSERT INTO Game_classes (game_id, title, value)
                  VALUES (?, ?, ?)""",
                [game_id, title, value])

db.commit()
db.close()
