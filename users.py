"""Module with user related SQL-queries."""

import sqlite3
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import db

# all database queries relating to users

def get_all_dev_game_classes(user_id): # gets the classes for every game for a single developer
    sql = """SELECT a.game_id AS game_id, a.title AS title, a.value AS value
             FROM game_classes a LEFT JOIN games b ON a.game_id = b.id
             WHERE b.user_id = ?"""
    result = db.query(sql, [user_id])

    all_dev_game_classes = {}
    for game_id, title, value in result:
        if game_id not in all_dev_game_classes:
            all_dev_game_classes[game_id] = {}
        if title not in all_dev_game_classes[game_id]:
            all_dev_game_classes[game_id][title] = []
        all_dev_game_classes[game_id][title].append(value)

    return all_dev_game_classes

def create_user(username, password, developer): # adding a user to the database
    password_hash = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username, password_hash, developer) VALUES (?, ?, ?)"
        db.execute(sql, [username, password_hash, developer])
        return True
    except sqlite3.IntegrityError:
        return False

def check_login(username, password): # checks the login of a user
    sql = "SELECT password_hash, id AS user_id, developer FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if result:
        return result[0] if check_password_hash(result[0]["password_hash"], password) else None
    return None


def get_user(user_id): # users username and developer status
    sql = """SELECT id, username, developer, image IS NOT NULL has_image
             FROM users
             WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_reviews(user_id): # users given reviews
    sql = """SELECT r.id, r.game_id, g.title AS game_title, r.sent_at, r.content, r.score
             FROM reviews r LEFT JOIN games g ON r.game_id = g.id
             WHERE r.user_id = ?
             ORDER BY r.sent_at DESC"""
    return db.query(sql, [user_id])

def get_games(user_id): # developers published games
    sql = """SELECT g.id, g.title, g.description, COUNT(r.id) AS total,
                    g.uploaded_at, g.user_id, u.username,
                    ROUND(1.0*SUM(r.score) / COUNT(r.id), 1) AS average
             FROM games g
                 LEFT JOIN reviews r ON g.id = r.game_id
                 LEFT JOIN users u ON g.user_id = u.id
             WHERE g.user_id = ?
             GROUP BY g.id
             ORDER BY g.id DESC"""
    return db.query(sql, [user_id])

def update_profile_picture(user_id, image): # updates the users profile picture
    sql = "UPDATE users SET image = ? WHERE id = ?"
    db.execute(sql, [image, user_id])

def get_profile_picture(user_id): # fetches the users profile picture
    sql = "SELECT image FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0][0] if result else None
