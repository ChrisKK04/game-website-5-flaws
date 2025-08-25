"""Main application file for the web server."""

import math
import secrets
import sqlite3
import time

from flask import (
    abort,
    flash,
    g,
    make_response,
    redirect,
    render_template,
    request,
    session,
    Flask
)
import markupsafe

import config
import db
import forum
import searching
import users

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

IMAGE_FORM = config.IMAGE_FORM
REVIEW_FORM = config.REVIEW_FORM
GAME_FORM = config.GAME_FORM
USER_FORM = config.USER_FORM
CATEGORIES_PER_LINE = config.CATEGORIES_PER_LINE
BLOCK_NEXT_PAGE_REDIRECT = config.BLOCK_NEXT_PAGE_REDIRECT
ROWS_COLS = config.ROWS_COLS

def require_login(): # checks login
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

def valid_user(username, password, developer): # checks user requirements
    if (not username or not password or not developer
        or len(username) > USER_FORM["MAX_USERNAME_LENGTH"]
        or len(password) > USER_FORM["MAX_PASSWORD_LENGTH"]):
        return True
    return False

def valid_game(title, description): # checks game requirements
    if (not title or not description
        or len(title) > GAME_FORM["MAX_TITLE_LENGTH"]
        or len(description) > GAME_FORM["MAX_DESCRIPTION_LENGTH"]):
        return True
    return False

def valid_review(content, score): # checks review requirements
    scores = ([str(score) for score
               in range(REVIEW_FORM["MIN_SCORE"], REVIEW_FORM["MAX_SCORE"] + 1)])
    if not content or len(content) > REVIEW_FORM["MAX_LENGTH"] or score not in scores:
        return True
    return False

@app.before_request # time tester (begin)
def before_request():
    g.start_time = time.time()

@app.after_request # time tester (end)
def after_request(response):
    elapsed_time = round(time.time() - g.start_time, 2)
    print("elapsed time:", elapsed_time, "s")
    return response

@app.template_filter() # a template filter to show line breaks
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/", methods=["GET", "POST"]) # homepage and game upload
@app.route("/<int:page>", methods=["GET", "POST"])
def index(page=1):
    page_size = config.GAMES_PER_PAGE
    game_count = forum.game_count()
    page_count = math.ceil(game_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    all_classes = forum.get_all_classes()
    all_game_classes = forum.get_all_game_classes()
    games = forum.get_games(page, page_size)
    stats = forum.get_stats()

    if request.method == "GET":
        return render_template("index.html", page=page, page_count=page_count, games=games,
                               all_classes=all_classes, all_game_classes=all_game_classes,
                               filled={}, stats=stats, GAME_FORM=GAME_FORM,
                               IMAGE_FORM=IMAGE_FORM, ROWS_COLS=ROWS_COLS,
                               CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)

    if request.method == "POST":
        require_login()
        check_csrf()

        title = request.form["title"]
        description = request.form["description"]

        classes = []
        classes_save = {}
        for entry in request.form.getlist("classes"):
            if entry:
                class_title, class_value = entry.split(":")
                if class_title not in all_classes:
                    abort(403)
                if class_value not in all_classes[class_title]:
                    abort(403)
                if class_title not in classes_save:
                    classes_save[class_title] = []
                classes_save[class_title].append(class_value)
                classes.append((class_title, class_value))

        if valid_game(title, description):
            flash(f"""A game has to include a title
                  (max {GAME_FORM['MAX_TITLE_LENGTH']} characters) and a description
                  (max {GAME_FORM['MAX_DESCRIPTION_LENGTH']} characters)""")
            filled = {"title": title, "description": description, "classes": classes_save}
            return render_template("index.html", page=page, page_count=page_count, games=games,
                                   all_classes=all_classes, all_game_classes=all_game_classes,
                                   filled=filled, stats=stats, GAME_FORM=GAME_FORM,
                                   IMAGE_FORM=IMAGE_FORM, ROWS_COLS=ROWS_COLS,
                                   CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)

        images = []
        for file in request.files.getlist("images"):
            if not file:
                continue
            if not file.filename.endswith(".jpg"):
                flash("ERROR: One or more of the files are not .jpg-files")
                filled = {"title": title, "description": description, "classes": classes_save}
                return render_template("index.html", page=page, page_count=page_count, games=games,
                                       all_classes=all_classes, all_game_classes=all_game_classes,
                                       filled=filled, stats=stats, GAME_FORM=GAME_FORM,
                                       IMAGE_FORM=IMAGE_FORM, ROWS_COLS=ROWS_COLS,
                                       CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)
            image = file.read()
            if len(image) > IMAGE_FORM["MAX_IMAGE_SIZE"]:
                flash("ERROR: One or more of the images are too big")
                filled = {"title": title, "description": description, "classes": classes_save}
                return render_template("index.html", page=page, page_count=page_count, games=games,
                                       all_classes=all_classes, all_game_classes=all_game_classes,
                                       filled=filled, stats=stats, GAME_FORM=GAME_FORM,
                                       IMAGE_FORM=IMAGE_FORM, ROWS_COLS=ROWS_COLS,
                                       CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)
            images.append(image)

        user_id = session["user_id"]
        thread_id = forum.add_game(title, description, user_id, classes, images)
        return redirect("/game/" + str(thread_id))

    return redirect("/")

@app.route("/register", methods=["GET", "POST"]) # register page
def register():
    if request.method == "GET":
        return render_template("register.html", next_page=request.referrer,
                               filled={}, USER_FORM=USER_FORM)

    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        developer = request.form["developer"]
        next_page = request.form["next_page"]

        if valid_user(username, password1, developer):
            flash(f"""An acccount has to have a username
                  (max {USER_FORM['MAX_USERNAME_LENGTH']} characters), a password
                  (max {USER_FORM['MAX_PASSWORD_LENGTH']} characters) and a user type
                  (reviewer or developer)""")
            filled = {"username": username}
            return render_template("register.html", filled=filled, USER_FORM=USER_FORM)

        if password1 != password2:
            flash("ERROR: The passwords do not match")
            filled = {"username": username}
            return render_template("register.html", filled=filled, USER_FORM=USER_FORM)

        if users.create_user(username, password1, developer):
            session["username"] = username # Login the user
            session["developer"] = int(developer) # stores whether or not the user is a developer
            session["user_id"] = db.last_insert_id() # fetch the id
            session["csrf_token"] = secrets.token_hex(16) # generates a hidden csrf-session-token
            flash("Account created. You have been automatically logged in.")
            if "/login" in next_page or "/register" in next_page:
                return redirect("/")
            return redirect(next_page)

        flash("ERROR: The username is taken")
        filled = {"username": username}
        return render_template("register.html", next_page=next_page,
                               filled=filled, USER_FORM=USER_FORM)

    return redirect("/")

@app.route("/login", methods=["GET", "POST"]) # login page
def login():
    if request.method == "GET":
        return render_template("login.html", next_page=request.referrer, filled={})

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        next_page = request.form["next_page"]

        info = users.check_login(username, password)
        if info:
            session["username"] = username
            session["developer"] = info["developer"]
            session["user_id"] = info["user_id"]
            session["csrf_token"] = secrets.token_hex(16)
            flash("Logged in.")
            if "/register" in next_page or "/login" in next_page:
                return redirect("/")
            return redirect(next_page)

        flash("ERROR: Wrong username or password")
        filled = {"username": username}
        return render_template("login.html", next_page=next_page, filled=filled)

    return redirect("/")

@app.route("/logout") # logout handler
def logout():
    session.clear()
    flash("Logged out.")
    next_page = request.referrer

    for block in BLOCK_NEXT_PAGE_REDIRECT:
        if block in next_page:
            return redirect("/")
    return redirect(next_page)

@app.route("/game/<int:game_id>", methods=["GET", "POST"]) # game page and review upload
def show_game(game_id):
    game = forum.get_game(game_id)
    if not game:
        abort(404)
    average = forum.get_average_score(game_id)
    reviews = forum.get_reviews(game_id)
    classes = forum.get_classes(game_id)
    images = forum.get_images(game_id)

    if request.method == "GET":
        return render_template("game.html", game=game, average=average, reviews=reviews,
                               classes=classes, images=images, REVIEW_FORM=REVIEW_FORM,
                               ROWS_COLS=ROWS_COLS, CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)

    if request.method == "POST":
        require_login()
        check_csrf()

        content = request.form["content"]
        score = request.form["score"]
        user_id = session["user_id"]
        game_id = request.form["game_id"]
        if valid_review(content, score):
            flash(f"""A review has to include the review
                  (max {REVIEW_FORM['MAX_LENGTH']} characters) and a score
                  ({REVIEW_FORM['MIN_SCORE']}-{REVIEW_FORM['MAX_SCORE']})""")
            filled = {"content": content, "score": str(score)}
            return render_template("game.html", game=game, average=average, reviews=reviews,
                                   classes=classes, images=images, filled=filled,
                                   REVIEW_FORM=REVIEW_FORM, ROWS_COLS=ROWS_COLS,
                                   CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)

        previous_review = forum.previous_review(user_id, game_id)
        if previous_review is not None:
            flash(f"""You have a previous review on this game.
                  You can edit or delete the previous
                  <a href="/game/{game_id}#{previous_review['id']}">review</a>.""")
            filled = {"content": content, "score": str(score), "previous": True}
            return render_template("game.html", game=game, average=average, reviews=reviews,
                                   classes=classes, images=images, filled=filled,
                                   REVIEW_FORM=REVIEW_FORM, ROWS_COLS=ROWS_COLS,
                                   CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)

        try:
            forum.new_review(content, user_id, game_id, score)
        except sqlite3.IntegrityError:
            abort(403)

        return redirect("/game/" + str(game_id))

    return redirect("/")

@app.route("/image/<int:image_id>") # view a game image
def show_image(image_id):
    image = forum.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response

@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"]) # edit review
def edit_review(review_id):
    require_login()

    review = forum.get_review(review_id)
    if not review:
        abort(404)

    if review["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit_review.html", review=review, REVIEW_FORM=REVIEW_FORM,
                               ROWS_COLS=ROWS_COLS)

    if request.method == "POST":
        check_csrf()
        content = request.form["content"]
        score = request.form["score"]
        if valid_review(content, score):
            flash(f"""A review has to include the review
                  (max {REVIEW_FORM['MAX_LENGTH']} characters) and a score
                  ({REVIEW_FORM['MIN_SCORE']}-{REVIEW_FORM['MAX_SCORE']})""")
            filled = {"content": content, "score": str(score)}
            return render_template("edit_review.html", review=review,
                                   filled=filled, REVIEW_FORM=REVIEW_FORM, ROWS_COLS=ROWS_COLS)

        flash("Review edited")
        forum.edit_review(review["id"], content, score)
        return redirect("/game/" + str(review["game_id"]))

    return redirect("/")

@app.route("/delete_review/<int:review_id>", methods=["GET", "POST"]) # delete review
def delete_review(review_id):
    require_login()

    review = forum.get_review(review_id)
    if not review:
        abort(404)

    if review["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("delete_review.html", review=review, next_page=request.referrer)

    if request.method == "POST":
        check_csrf()
        flash("Review deleted")
        next_page = request.form["next_page"]
        if "delete" in request.form:
            forum.delete_review(review["id"])
        return redirect(next_page)

    return redirect("/")

@app.route("/edit_game/<int:game_id>", methods=["GET", "POST"]) # edit game
def edit_game(game_id):
    require_login()

    game = forum.get_game(game_id)
    if not game:
        abort(404)
    all_classes = forum.get_all_classes()

    if game["user_id"] != session["user_id"]:
        abort(403)

    classes = forum.get_classes(game_id)
    images = forum.get_images(game_id)

    if request.method == "GET":
        return render_template("edit_game.html", game=game, all_classes=all_classes,
                               classes=classes, images=images, filled={},
                               GAME_FORM=GAME_FORM, IMAGE_FORM=IMAGE_FORM, ROWS_COLS=ROWS_COLS,
                               CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)

    if request.method == "POST":
        check_csrf()
        title = request.form["title"]
        description = request.form["description"]

        classes = []
        classes_save = {}
        for entry in request.form.getlist("classes"):
            if entry:
                class_title, class_value = entry.split(":")
                if class_title not in all_classes:
                    abort(403)
                if class_value not in all_classes[class_title]:
                    abort(403)
                if class_title not in classes_save:
                    classes_save[class_title] = []
                classes_save[class_title].append(class_value)
                classes.append((class_title, class_value))

        delete_images = request.form.getlist("delete_images")
        new_images = []
        for file in request.files.getlist("new_images"):
            if not file:
                continue
            if not file.filename.endswith(".jpg"):
                flash("ERROR: One or more of the files are not .jpg-files")
                filled = {"title": title, "description": description, "classes": classes_save}
                return render_template("edit_game.html", game=game, all_classes=all_classes,
                                       classes=classes, images=images, filled=filled,
                                       GAME_FORM=GAME_FORM, IMAGE_FORM=IMAGE_FORM,
                                       ROWS_COLS=ROWS_COLS,
                                       CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)
            image = file.read()
            if len(image) > IMAGE_FORM["MAX_IMAGE_SIZE"]:
                flash("ERROR: One or more of the images are too big")
                filled = {"title": title, "description": description, "classes": classes_save}
                return render_template("edit_game.html", game=game, all_classes=all_classes,
                                       classes=classes, images=images, filled=filled,
                                       GAME_FORM=GAME_FORM, IMAGE_FORM=IMAGE_FORM,
                                       ROWS_COLS=ROWS_COLS,
                                       CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)
            new_images.append(image)

        if valid_game(title, description):
            flash(f"""A game has to include a title
                  (max {GAME_FORM['MAX_TITLE_LENGTH']} characters) and a description
                  (max {GAME_FORM['MAX_DESCRIPTION_LENGTH']} characters)""")
            filled = {"title": title, "description": description, "classes": classes_save}
            return render_template("edit_game.html", game=game, all_classes=all_classes,
                                   classes=classes, images=images, filled=filled,
                                   GAME_FORM=GAME_FORM, IMAGE_FORM=IMAGE_FORM,
                                   ROWS_COLS=ROWS_COLS,
                                   CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)

        flash("Game edited")
        forum.edit_game(game["id"], title, description, classes, delete_images, new_images)
        return redirect("/game/" + str(game["id"]))

    return redirect("/")

@app.route("/delete_game/<int:game_id>", methods=["GET", "POST"]) # delete game
def delete_game(game_id):
    require_login()

    game = forum.get_game(game_id)
    if not game:
        abort(404)

    if game["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("delete_game.html", game=game, next_page=request.referrer)

    if request.method == "POST":
        check_csrf()
        next_page = request.form["next_page"]
        flash("Game deleted")
        if "delete" in request.form:
            forum.delete_game(game["id"])
        if "/game" in next_page:
            return redirect("/")
        return redirect(next_page)

    return redirect("/")

@app.route("/user/<int:user_id>") # user page
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(403)

    if user["developer"] == 0: # user
        reviews = users.get_reviews(user_id)
        return render_template("user.html", user=user, reviews=reviews,
                               CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)
    if user["developer"] == 1: # developer
        games = users.get_games(user_id)
        all_dev_game_classes = users.get_all_dev_game_classes(user_id)
        return render_template("user.html", user=user, games=games,
                               all_dev_game_classes=all_dev_game_classes,
                               CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)

    return redirect("/")

@app.route("/update_profile_picture", methods=["GET", "POST"]) # update profile picture
def update_profile_picture():
    require_login()

    if request.method == "GET":
        return render_template("update_profile_picture.html", IMAGE_FORM=IMAGE_FORM)

    if request.method == "POST":
        check_csrf()
        file = request.files["image"]
        if not file.filename.endswith(".jpg"):
            flash("ERROR: The file is not a .jpg-file")
            return redirect("/update_profile_picture")

        image = file.read()
        if len(image) > IMAGE_FORM["MAX_IMAGE_SIZE"]:
            flash("ERROR: The image is too big")
            return redirect("/update_profile_picture")

        user_id = session["user_id"]
        users.update_profile_picture(user_id, image)
        return redirect("/user/" + str(user_id))

    return redirect("/")

@app.route("/profile_picture/<int:user_id>") # view a profile picture
def show_profile_picture(user_id):
    image = users.get_profile_picture(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response

@app.route("/search") # search page:
def search():
    search_type = request.args.get("search_type")
    all_classes = forum.get_all_classes()

    if search_type == "game_search":
        title = request.args.get("title")
        description = request.args.get("description")
        game_score_type = int(request.args.get("game_score_type"))
        game_score = float(request.args.get("game_score")) if request.args.get("game_score") else 1
        publisher = request.args.get("publisher")

        classes = []
        classes_save = {}
        for entry in request.args.getlist("classes"):
            if entry:
                class_title, class_value = entry.split(":")
                if class_title not in all_classes:
                    abort(403)
                if class_value not in all_classes[class_title]:
                    abort(403)
                if class_title not in classes_save:
                    classes_save[class_title] = []
                classes_save[class_title].append(class_value)
                classes.append((class_title, class_value))

        games_filled = {"title": title, "description": description,
                        "game_score_type": str(game_score_type), "game_score": game_score,
                        "publisher": publisher, "classes_save": classes_save}

        games, result_classes, valid_game_ids = searching.games(title, description,
                                                                game_score_type, game_score,
                                                                publisher, classes)
        return render_template("search.html", all_classes=all_classes, games=games,
                               result_classes=result_classes, valid_game_ids=valid_game_ids,
                               games_filled=games_filled, ROWS_COLS=ROWS_COLS,
                               CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)

    if search_type == "review_search":
        content = request.args.get("content")
        review_score_type = int(request.args.get("review_score_type"))
        review_score = int(request.args.get("review_score"))

        reviews_filled = {"content": content, "review_score_type": str(review_score_type),
                          "review_score": str(review_score)}

        reviews = searching.reviews(content, review_score_type, review_score)
        return render_template("search.html", all_classes=all_classes, reviews=reviews,
                               reviews_filled=reviews_filled, ROWS_COLS=ROWS_COLS,
                               CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)

    if search_type == "user_search":
        username = request.args.get("username")
        user_type = int(request.args.get("user_type"))

        users_filled = {"username": username, "user_type": str(user_type)}

        users_list = searching.users(username, user_type)
        return render_template("search.html", all_classes=all_classes, users=users_list,
                               users_filled=users_filled, ROWS_COLS=ROWS_COLS,
                               CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)

    no_search = True
    return render_template("search.html", all_classes=all_classes, no_search=no_search,
                           ROWS_COLS=ROWS_COLS, CATEGORIES_PER_LINE=CATEGORIES_PER_LINE)
