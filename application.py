# must run in cmd venv before start
# $Env:FLASK_APP="application.py"
# $Env:FLASK_DEBUG=1


# for Postgress DB later
# import psycopg2
import os
import datetime
# import psycopg2


# for my local env variable and api key
from dotenv import load_dotenv
project_folder = os.path.expanduser('./')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory, jsonify
from flask_session import Session
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from operator import itemgetter
from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)
# args to access the build folder of react app idle trillionaire
# app = Flask(__name__ ,static_folder='client/build',static_url_path='') 

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'legitdev2fr34gjkf7Hfi9G'
Session(app)

db = SQL(os.getenv("DATABASE_URL"))
# for postgress of heroku deployment

os.environ["DEBUSSY"] = "1"

# gets a json with data
@login_required
@app.route('/serverAI')
def serverAI():
    userID = session["user_id"]
    username = db.execute("SELECT username FROM users WHERE id = :id", id=userID)[0]['username']
    print(username)

    newItem = request.args.get('newItem', 0, type=str)
    b = request.args.get('b', 0, type=str)

    result = newItem + ' ' + b

    db.execute("INSERT INTO inventory (id, username, itemname) VALUES(?, ?, ?)", userID, username, result)
    return jsonify(result=result)

@app.route("/")
@login_required
def index():
    if request.method == "GET":
        
        userId = session["user_id"]
        userdata = db.execute("SELECT * FROM users WHERE id = :user", user=userId)
        inventory = db.execute("SELECT * FROM inventory WHERE id = :id", id=userId)
        # make list of inventory
        listInv = []
        for i, row in enumerate(inventory):
            invdata = inventory[i]['itemname']
            listInv.append(invdata)

        print(listInv, "listInv")

    return render_template("index.html", userdata=userdata, listInv=listInv)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    return redirect("/")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Remember user id that has logged in
        try:
            session["user_id"] = rows[0]["id"]
        except:
            return apology("invalid username or password", 403)


        # username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form.get('username')
        slogan = request.form.get('slogan')
        alignment = request.form.get('alignment')
        race = request.form.get('race')
        startItem = request.form.get('startItem')
        registerpassword1 = request.form.get('registerpassword1')
        registerpassword2 = request.form.get('registerpassword2')
        PWhash = generate_password_hash(registerpassword1)
        registeredUsers = db.execute("SELECT username FROM users")

        if len(username) > 14:
            return apology("username max 14 chars")
        if not username:
            return apology("you need a name pal")
        if not slogan:
            return apology("enter a slogan bud")
        if not alignment:
            return apology("pick a alignment")
        if not race:
            return apology("pick a race")
        if not registerpassword1:
            return apology("did not enter password")
        if not registerpassword2:
            return apology("did not enter retyped password")
        if registerpassword1 != registerpassword2 :
            return apology("passwords did not match")

        if db.execute("SELECT * FROM users WHERE username = :username",
            username=request.form.get("username")):
            return apology("that username is taken")
        db.execute("INSERT INTO users (username, hash, slogan, alignment, race) VALUES(?, ?, ?, ?, ?)", username, PWhash, slogan, alignment, race)

        userID = int(db.execute("SELECT id FROM users WHERE username = :userName", userName=username)[0]['id'])
    
        db.execute("INSERT INTO inventory (id, username, itemname, quantity) VALUES(?, ?, ?, ?)", userID, username, startItem, 1)

        return redirect("/")




@app.route("/showusers", methods=["GET", "POST"])
def showusers():
    if request.method == "GET":
        users = db.execute("SELECT * FROM users")
        # print('listusers ',users)
        listUsers = []
        for user in users:
            userdata = list((user['id'] ,user['username'], user['slogan'], user['alignment'], user['race'] ))
            listUsers.append(userdata)

    return render_template("showusers.html", listUsers=listUsers)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# for development
# if __name__ == '__main__':
#     app.run(debug=True)

# for production
if __name__ == '__main__':
 app.debug = False
 port = int(os.environ.get("PORT", 8080))
 app.run(host="0.0.0.0", port=port)
