"""Module to make SQL-queries easier make."""

import sqlite3

from flask import g

# forming a connection to the database
def get_connection():
    con = sqlite3.connect("database.db") # form a connection to the database
    con.execute("PRAGMA foreign_keys = ON") # make rows secure
    con.row_factory = sqlite3.Row # make referencing columns with their names possible
    return con # return the connection

# INSERT, UPDATE, DELETE
def execute(sql, params=[]):
    con = get_connection() # form a connection
    try: # try to execute
        result = con.execute(sql, params) # execute
        con.commit() # commit changes
        g.last_insert_id = result.lastrowid # get the id of the last added row
    finally: # do everytime no matter if a command fails
        con.close() # close the connection

# Without the finally clause, the database will not be closed right away if an error occurs
# and the website could crash.

# ID of the last changed row
def last_insert_id():
    return g.last_insert_id # fetching the ID of the last added row

# SELECT
def query(sql, params=[]):
    con = get_connection() # form a connection
    result = con.execute(sql, params).fetchall() # fetch all of the relevant rows
    con.close() # close the connection
    return result # return the result
