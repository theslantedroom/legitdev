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
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from operator import itemgetter
from helpers import apology, login_required, lookup, usd, lookupLeader

# Configure application
app = Flask(__name__)

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



# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")

os.environ["DEBUSSY"] = "1"


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    userId = session["user_id"]
    # Query  database for INFO
    rows = db.execute("SELECT * FROM portfolio WHERE id = :user",
                          user=userId)
    cash = db.execute("SELECT cash FROM users WHERE id = :user",
                          user=userId)[0]['cash']
    username = db.execute("SELECT username FROM users WHERE id = :user",
                          user=userId)[0]['username']

    # pass  list of lists to the template page
    total = cash
    stocks = []

    for index, row in enumerate(rows):
        details = lookup(row['symbol'])

        # create a list
        currentStock = list((details['symbol'], details['name'], row['shares'], details['price'], round(details['price'] * row['shares'], 2)))
        # add the list to the stocks list
        stocks.append(currentStock)
        total += stocks[index][4]

    stocksConverted = stocks
    for key, stock in enumerate(stocks):
        # convert to formated string fro display
        stocksConverted[key][3] = "${:,.2f}".format(stocks[key][3])
        stocksConverted[key][4] = "${:,.2f}".format(stocks[key][4])

    cashConverted = "${:,.2f}".format(cash)
    totalConverted = "${:,.2f}".format(total)

    return render_template("index.html", stocks=stocksConverted, cash=cashConverted, total=totalConverted, username=username)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")

    if request.method == "POST":
        # store data from buy form
        Userid = session["user_id"]

        stringAmount = request.form.get("amount")

        try:
            if float(stringAmount) < 0:
                # print(1)
                return apology("Must buy at least one stock")
        except:
            # print(2)
            return apology("Must buy at least one stock", 400)

        symbol = request.form.get("symbol").upper()

        try:
            buyCount = float(stringAmount)
        except:
            # print(3)
            return apology("Must buy at least one stock")

        if not lookup(symbol):
            # print(4)
            return apology("Could not find the stock")

        username = str(db.execute("SELECT username FROM users WHERE id = :id", id=Userid)[0]['username'])

        # Calculate total value of the transaction
        bookcost = lookup(symbol)['price']
        company = lookup(symbol)['name']
        totalCost = buyCount * bookcost

        # Check if current CASH is enough
        currentCash = db.execute("SELECT cash FROM users WHERE id = :user", user=Userid)[0]['cash']
        # print(currentCash)
        if currentCash < totalCost:
            return apology("You don't have enough money")

        # Check if user already owns this stocks
        stocktobuy = db.execute("SELECT shares FROM portfolio WHERE id = :id AND symbol = :symbol", id=Userid, symbol=symbol)
        # print(stocktobuy)

        # Insert new row into the stock table
        if not stocktobuy:
            db.execute("INSERT INTO portfolio(id, username, symbol, stockname, shares) VALUES (:id, :username, :symbol, :stockname, :shares)",
                        id=Userid, username=username, symbol=symbol, stockname=company, shares=buyCount)
            # update caluated values
            # bookcost = 0
            # total = 0
        #add to existing holdings
        else:
            newTotal = buyCount
            newTotal += stocktobuy[0]['shares']
            db.execute("UPDATE portfolio SET shares = :shares WHERE id = :id AND symbol = :symbol",
                id=Userid, symbol=symbol, shares=newTotal)

        # update user cash
        remainingCash = round((currentCash - totalCost),2)
        db.execute("UPDATE users SET cash = :cash WHERE id = :user", cash=remainingCash, user=Userid)

        # Update history table
        db.execute("INSERT INTO history(id, symbol, shares, value) VALUES (:id, :symbol, :shares, :value)",
                id=Userid, symbol=symbol, shares=buyCount, value=totalCost)

        return redirect("/")

@app.route("/history")
@login_required
def history():
    Userid = session["user_id"]
    """Show history of transactions"""

    # query database with the transactions history
    rows = db.execute("SELECT * FROM history WHERE id = :id", id=Userid)

    # pass a list of lists to the template page
    history = []
    for row in rows:
        tradeDetails = lookup(row['symbol'])
        trade = list((tradeDetails['symbol'], tradeDetails['name'], row['shares'], "${:,.2f}".format(row['value']), row['date']))
        history.append(trade)


    # redirect user to index page
    return render_template("history.html", history=history)

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

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html", stock="")

    if request.method == "POST":
        stock = lookup(request.form.get("stock"))
        if not stock:
            return apology("That stock does not exist")

        return render_template("quote.html", stock=stock)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form.get('username')
        registerpassword1 = request.form.get('registerpassword1')
        registerpassword2 = request.form.get('registerpassword2')
        PWhash = generate_password_hash(registerpassword1)
        registeredUsers = db.execute("SELECT username FROM users")

        print(registeredUsers)
        if len(username) >= 14:
            return apology("username max 14 chars")
        if not username:
            return apology("no username")
        if not registerpassword1:
            return apology("did not enter password")
        if not registerpassword2:
            return apology("did not enter retyped password")
        if registerpassword1 != registerpassword2 :
            return apology("passwords did not match")

        if db.execute("SELECT * FROM users WHERE username = :username",
            username=request.form.get("username")):
            return apology("Username taken")

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, PWhash)

        return redirect("/")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    userid = session["user_id"]
    """Sell shares of stock"""
    if request.method == "GET":
        # query database with the transactions history
        rows = db.execute("SELECT symbol, shares FROM portfolio WHERE id = :userid", userid=userid)

        # create a dictionary with the availability of the stocks
        stocksHeld = {}
        for row in rows:
            stocksHeld[row['symbol']] = row['shares']

        return render_template("sell.html", stocksHeld=stocksHeld)

    if request.method == "POST":
        Userid = session["user_id"]
        # collect relevant informations
        try:
            sellCount=int(request.form.get("sellCount"))
        except:
            return apology("you must sell at least 0ne stock")
        symbol=request.form.get("symbol")
        price=lookup(symbol)["price"]
        value=round(price*sellCount)

        # Update portfolio table
        heldbefore = db.execute("SELECT shares FROM portfolio WHERE id = :user AND symbol = :symbol", symbol=symbol, user=Userid)[0]['shares']
        heldafter = heldbefore - sellCount

        # stop the transaction if the user does not have enough stocks
        if heldafter < 0:
            return apology("You hold that stock, but not that many!")

        # delete stock from table if we sold out all stocks
        if heldafter == 0:
            db.execute("DELETE FROM portfolio WHERE id = :user AND symbol = :symbol", symbol=symbol, user=Userid)
        # else update with new count
        else:
            db.execute("UPDATE portfolio SET shares = :shares WHERE id = :user AND symbol = :symbol",
                          symbol=symbol, user=Userid, shares=heldafter)
        #update user's cash
        cash = db.execute("SELECT cash FROM users WHERE id = :user",
                          user=Userid)[0]['cash']
        cashRemaining = cash + (price * sellCount)
        db.execute("UPDATE users SET cash = :cash WHERE id = :user",
                          cash=cashRemaining, user=Userid)
        # Update history table
        db.execute("INSERT INTO history(id, symbol, shares, value) VALUES (:id, :symbol, :shares, :value)",
                id=Userid, symbol=symbol, shares=-sellCount, value=value)

        return redirect("/")


@app.route("/leaderboard", methods=["GET", "POST"])
def leaderboard():

    if request.method == "GET":
        users = db.execute("SELECT username, id FROM users")
        # print('listusers ',users)
        listUsers = []
        for user in users:
            userdata = list((user['username'], user['id']))
            listUsers.append(userdata)
        # query database for a list of all the users /list of dicts

        # for user in listUsers:
        #     holdingValue = 0
        #     holdings = db.execute("SELECT shares, symbol FROM portfolio WHERE username = :username", username=user[0])
        #     for stock in holdings:
        #         stockPrice = lookupLeader(stock['symbol'])
        #         value = stock['shares'] * stockPrice
        #         holdingValue += value
        #         user[1] = round(holdingValue, 2)

        # for user in listUsers:
        #     net = round(user[2] + user[1],0)
        #     user[3] = "${:,.0f}".format(user[1])
        #     user[4] = "${:,.0f}".format(user[2])
        #     user[5] = "${:,.0f}".format(net)
        #     user[6] = net

        # sortedLeader = sorted(listUsers, key=itemgetter(6), reverse=True)
        # # print(listUsers)

    return render_template("leaderboard.html", listUsers=listUsers)

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
