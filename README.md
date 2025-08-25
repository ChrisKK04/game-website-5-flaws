# Purple

**Purple** is a website where developers can publish their games and reviewers can leave reviews for their favorite games.

**Note**: Development on this project officially ended on **June 29, 2025**. This repository is no longer actively maintained.

## Features

* Creating an account and logging in
* Uploading games with a title and description alongside optional sections for categories and images
* Leaving reviews and scores on games
* Editing and deleting reviews and games
* Seeing the posts of other users
* User pages which list a given user's posts and certain statistics about the user
* Game, review and user search
* Beautiful CSS styling

## Using the website (Linux/Windows with Git Bash)

(The website requires [Python](https://www.python.org/) and [SQLite](https://sqlite.org/) to function).

First, create a folder for the website. Then, copy all the files from this repository into that folder.

Now, run the following commands in the terminal whilst being in the created folder:  

Create a virtual Python environment to download the necessary packages into:
```
$ python3 -m venv venv
```
Activate the virtual environment  
Linux:
```
$ source venv/bin/activate
```
Windows with Git Bash:
```
$ source venv/Scripts/activate
```
Download and install flask:
```
$ pip install flask
```
Create database.db with the necessary tables and indexes:
```
$ sqlite3 database.db < schema.sql
```
Insert the classes:
```
$ sqlite3 database.db < init.sql
```

After running the commands, the database will be empty and you can start using the website. Optionally, you can insert some data for testing by running a Python script.

pre_data.py: populates the database with some games, users and reviews.

Login to accounts:
```
Username: Jason, RampageGames            # uppercase starts
Password: jason, rampagegames            # all lowercase
```

seed.py: populates the database with a large dataset for peformance testing.

config.py: is a file that includes many global variables alongside their presets. The variable values can be freely adjusted.

Time zone: TIME is a global time zone variable that adjusts the time in SQL queries from UTC 0.  
Secret key: SECRET_KEY is the secret key (session key) of the website.  
Data restriction: for example REVIEW_FORM["MAX_SCORE"] sets the highest score that can be given to a game.
```
TIME = '+3 hours'
SECRET_KEY = ...
"MAX_SCORE": 5
```

You can now use the website in the terminal with:

(A fetch-to-load time measurement is also displayed in the terminal).
```
$ flask run                              # runs the website
$ ctrl + c                               # closes the website
```

# Website performance with large datasets

A large dataset for performance testing was generated with the script in seed.py.

## Performance without optimizations

**Parameters:**
* `user_count = 1000`
* `game_count = 10⁵`
* `review_count = 10⁶`
* `game_classes = 10⁵`

**Result:**
The homepage loading time averaged around **14 s**.

## Optimizations done
* Added pagination to the homepage
* Added indexes to the database

## Performance after optimizations

**Parameters:**
* `user_count = 1000`
* `game_count = 10⁵`
* `review_count = 10⁶`
* `game_classes = 10⁵`

**Result:**
The homepage (/1) had an average loading time of around 0.5 seconds, while page 10 000 (/10000) averaged about 3 to 4 seconds. Loading pages with higher indexes takes longer because the homepage pagination relies on SQL queries using LIMIT/OFFSET clauses, which must skip over many rows when loading pages with large offsets.

# Image sources
- Favicon: [Nintendo Gameboy vector on Pixabay](https://pixabay.com/vectors/nintendo-gameboy-gameboy-nintendo-4003938/)