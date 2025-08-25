"""Module with forum related SQL-queries."""

import db
import config

# this global variable changes the default sql time zone from UTC+0 to UTC+3
# it can be freely changed
TIME = config.TIME

# all database queries relating to the forum

def get_stats(): # amount of games, reviews and users
    sql = """SELECT
                (SELECT COUNT(id) FROM games) AS games_amount,
                (SELECT COUNT(id) FROM reviews) AS reviews_amount,
                (SELECT COUNT(id) FROM users WHERE developer = 1) AS developers_amount,
                (SELECT COUNT(id) FROM users WHERE developer = 0) AS reviewers_amount"""
    return db.query(sql)[0]

def get_classes(game_id): # gets all of an id-specified games classes
    sql = "SELECT title, value FROM game_classes WHERE game_id = ? ORDER BY LOWER(value)"
    result = db.query(sql, [game_id])

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def get_all_classes(): # gets all of the classes from the database into a dictionary
    sql = "SELECT title, value FROM classes ORDER BY LOWER(value)"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def get_all_game_classes(): # gets the classes for every game into a dictionary
    # all_game_classes[game_id] = classes
    sql = "SELECT game_id, title, value FROM game_classes"
    result = db.query(sql)

    all_game_classes = {}
    for game_id, title, value in result:
        if game_id not in all_game_classes:
            all_game_classes[game_id] = {}
        if title not in all_game_classes[game_id]:
            all_game_classes[game_id][title] = []
        all_game_classes[game_id][title].append(value)

    return all_game_classes

def get_images(game_id): # gets all of the images for a game
    sql = "SELECT id from images WHERE game_id = ?"
    return db.query(sql, [game_id])

def get_image(image_id): # gets the id-specified image
    sql = "SELECT image FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    return result[0][0] if result else None

def get_games(page, page_size): # fetches all of the games and their info
    sql = """SELECT g.id, g.title, g.description, COUNT(r.id) AS total, g.uploaded_at,
                    g.user_id, u.username, ROUND(1.0*SUM(r.score) / COUNT(r.id), 1) AS average
             FROM games g
             LEFT JOIN reviews r ON g.id = r.game_id
             LEFT JOIN users u on g.user_id = u.id
             GROUP BY g.id
             ORDER BY g.id DESC
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])

def get_game(game_id): # fetches an id-specified game
    sql = """SELECT g.id, g.title, g.description, g.uploaded_at, g.user_id, u.username
             FROM games g LEFT JOIN users u ON g.user_id = u.id
             WHERE g.id = ?"""
    result = db.query(sql, [game_id])
    return result[0] if result else None # none if no matches

def get_average_score(game_id): # fetches an id-specified games average user-score
    sql = """SELECT ROUND(1.0*SUM(r.score) / COUNT(r.id), 1) AS average
             FROM games g LEFT JOIN reviews r ON r.game_id = g.id
             WHERE g.id = ?"""
    result = db.query(sql, [game_id])
    return result[0] if result else None # none if no matches

def add_game(title, description, user_id, classes, images): # adds a game
    sql = f"""INSERT INTO games (title, description, uploaded_at, user_id)
              VALUES (?, ?, datetime('now', '{TIME}'), ?)"""
    db.execute(sql, [title, description, user_id])

    game_id = db.last_insert_id()

    sql = "INSERT INTO game_classes (game_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [game_id, class_title, class_value])

    sql = "INSERT INTO images (game_id, image) VALUES (?, ?)"
    for image in images:
        db.execute(sql, [game_id, image])

    return game_id

def get_reviews(game_id): # fetches all reviews for an id-specified game
    sql = """SELECT r.id, r.content, r.sent_at, r.user_id, r.score, u.username, u.image
             FROM reviews r LEFT JOIN users u ON r.user_id = u.id
             WHERE r.game_id = ?
             ORDER BY r.sent_at DESC"""
    return db.query(sql, [game_id])

def new_review(content, user_id, game_id, score): # adds a new review for a game
    sql = f"""INSERT INTO reviews (content, sent_at, user_id, game_id, score)
              VALUES (?, datetime('now', '{TIME}'), ?, ?, ?)"""
    db.execute(sql, [content, user_id, game_id, score])

def get_review(review_id): # returns a review's id and contents with it's id
    sql = """SELECT r.id, r.game_id, r.content, r.user_id, r.score, g.title
             FROM reviews r
             LEFT JOIN games g ON r.game_id = g.id
             WHERE r.id = ?"""
    result = db.query(sql, [review_id])
    return result[0] if result else None # none if no matches

def previous_review(user_id, game_id): # checks if there is a previous review for the same game
    # if review -> returns it's id else -> returns nothing
    sql = """SELECT r.id
             FROM reviews r LEFT JOIN games g ON r.game_id = g.id
             WHERE r.user_id = ? AND g.id = ?"""
    result = db.query(sql, [user_id, game_id])
    return result[0] if result else None

def edit_review(review_id, content, score): # updates a review
    sql = "UPDATE reviews SET content = ?, score = ? WHERE id = ?"
    db.execute(sql, [content, score, review_id])

def delete_review(review_id): # deletes a review
    sql = "DELETE FROM reviews WHERE id = ?"
    db.execute(sql, [review_id])

def edit_game(game_id, title, description, classes, delete_images, new_images): # updates a game
    sql = "UPDATE games SET title = ?, description = ? WHERE id = ?"
    db.execute(sql, [title, description, game_id])

    sql = "DELETE FROM game_classes WHERE game_id = ?"
    db.execute(sql, [game_id])
    sql = "INSERT INTO game_classes (game_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [game_id, class_title, class_value])

    sql = "DELETE FROM images WHERE id = ?"
    for image_id in delete_images:
        db.execute(sql, [image_id])

    sql = "INSERT INTO images (game_id, image) VALUES (?, ?)"
    for image in new_images:
        db.execute(sql, [game_id, image])

def delete_game(game_id): # deletes a game
    sql = "DELETE FROM games WHERE id = ?"
    db.execute(sql, [game_id])

def game_count(): # amount of games in the database
    sql = "SELECT COUNT(id) FROM games"
    return db.query(sql)[0][0]
