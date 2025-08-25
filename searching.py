"""Module with searching related SQL-queries."""

import db

# all database queries relating to searching

def games(title_sql, description, game_score_type, game_score, publisher, classes):
    sql = """SELECT g.id AS game_id, g.title, g.description, u.id AS publisher_id,
                    u.username AS publisher, g.uploaded_at, COUNT(r.id) AS total,
                    ROUND(1.0*SUM(r.score) / COUNT(r.id), 1) AS average
             FROM games g
                  LEFT JOIN users u ON g.user_id = u.id
                  LEFT JOIN reviews r ON g.id = r.game_id
             WHERE g.title LIKE ? AND g.description LIKE ? AND u.username LIKE ?
             GROUP BY g.id"""
    parameters = ["%" + title_sql + "%", "%" + description + "%", "%" + publisher + "%"]
    if game_score_type == 1:
        sql += " HAVING ROUND(1.0*SUM(r.score) / COUNT(r.id), 1) >= ?"
        parameters.append(game_score)
    elif game_score_type == 2:
        sql += " HAVING ROUND(1.0*SUM(r.score) / COUNT(r.id), 1) <= ?"
        parameters.append(game_score)

    sql += " ORDER BY g.id DESC"
    games_list = db.query(sql, parameters) # get the matching games (no classes)

    game_ids = [game['game_id'] for game in games_list] # get the ids of the matching games
    set_classes = set(classes) # make a set of the classes in the search
    valid_game_ids = [] # list of game ids for which the games have the classes in the search

    result_classes = {} # classes for games - result_classes[game_id] = [<list of classes>]
    for game_id in game_ids:
        set_classes_check = set() # make a set for class comparing
        sql = "SELECT title, value FROM game_classes WHERE game_id = ? ORDER BY LOWER(value)"
        result = db.query(sql, [game_id])
        for title, value in result:
            if game_id not in result_classes:
                result_classes[game_id] = {}
            if title not in result_classes[game_id]:
                result_classes[game_id][title] = []
            if value not in result_classes[game_id][title]:
                result_classes[game_id][title].append(value)
            set_classes_check.add((title, value)) # add the classes title and value
        if game_id not in result_classes: # if the game doesn't have any classes
            result_classes[game_id] = "no_classes"
        # if the game's classes are a superset of the classes in the search = matches search
        if set_classes <= set_classes_check:
            valid_game_ids.append(game_id)

    # games = games that match the search (no classes)
    # result_classes = the classes for every game in games
    # valid_game_ids = the ids of games that include the classes of the search
    return (games_list, result_classes, valid_game_ids)

def reviews(content, review_score_type, review_score):
    sql = """SELECT u.id AS user_id, u.username, g.id AS game_id, g.title AS game_title,
                    r.id AS review_id, r.sent_at, r.content, r.score
             FROM reviews r
                  LEFT JOIN games g ON r.game_id = g.id
                  LEFT JOIN users u ON r.user_id = u.id
             WHERE r.content LIKE ?"""
    if review_score_type == 0: # any score
        sql += " ORDER BY r.sent_at DESC"
        return db.query(sql, ["%" + content + "%"])
    if review_score_type == 1: # above the given score
        sql += " AND r.score >= ? ORDER BY r.sent_at DESC"
        return db.query(sql, ["%" + content + "%", review_score])
    if review_score_type == 2: # below the given score
        sql += " AND r.score <= ? ORDER BY r.sent_at DESC"
        return db.query(sql, ["%" + content + "%", review_score])

    return []

def users(username, user_type):
    if user_type == 2: # any
        sql = """SELECT id, username, developer, image
                 FROM users
                 WHERE username LIKE ?
                 ORDER BY developer DESC, username"""
        return db.query(sql, ["%" + username + "%"])

    if user_type == 0: # reviewer
        sql = """SELECT id, username, developer, image
                 FROM users
                 WHERE developer = 0 AND username LIKE ?
                 ORDER BY username"""
        return db.query(sql, ["%" + username + "%"])

    if user_type == 1: # developer
        sql = """SELECT id, username, developer, image
                 FROM users
                 WHERE developer = 1 AND username LIKE ?
                 ORDER BY username"""
        return db.query(sql, ["%" + username + "%"])

    return []
