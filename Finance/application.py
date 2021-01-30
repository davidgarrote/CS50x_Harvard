import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import hashlib, uuid
from helpers import apology, login_required, lookup, usd
import locale

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

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    
    """Show portfolio of stocks"""

    # Query infos from database
    rows = db.execute("SELECT id, username, stock, price, SUM(shares),total_spent, date FROM transactions WHERE id = :user GROUP BY stock",
                          user=session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = :user",
                          user=session["user_id"])[0]['cash']

    # pass a list of lists to the template page, template is going to iterate it to extract the data into a table
    total = cash
    stocks = []
    for index, row in enumerate(rows):
        stock_info = lookup(row['stock'])

        # create a list with all the info about the stock and append it to a list of every stock owned by the user
        stocks.append(list((stock_info['symbol'], stock_info['name'], row['SUM(shares)'], stock_info['price'], round(stock_info['price'] * row['SUM(shares)'], 2))))
        total += stocks[index][4]

    return render_template("index.html", stocks=stocks, cash=round(cash, 2), total=round(total, 2))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    
    """IF METHOD IS GET"""
    if request.method == "GET":
        return render_template("buy.html")
        
    """IF METHOD IS POST"""
    if request.method == "POST":
        
        """CHECK THAT STOCK SYMBOL EXISTS AND A VALID NUMBER OF SHARES WAS INTRODUCED"""
        
        if not request.form.get("symbol"):
            return apology("Please input a stock symbol", 207)
            
        elif not request.form.get("shares"):
            return apology("Please input a share amount", 207)
            
        elif not lookup(request.form.get("symbol")):
            return apology("Please input a valid symbol")
            
        elif int(request.form.get("shares")) < 1:
            return apology("Please input a valid amout of shares")
            
        else:
            
            buy_data = lookup(request.form.get("symbol"))
            price = buy_data["price"]
            total = price * float((request.form.get("shares")))
            
            """Open wallet and check if user has enough money to make the purchase"""
            wallet = db.execute("SELECT cash FROM users WHERE id = :user", user=session["user_id"])[0]['cash']
            if total > wallet:
                return ("Sorry not enough funds")
                
                
            else:
                
                """Define variables that we are going to use"""
                
                """Username definition"""
                rowss = db.execute("SELECT * FROM users WHERE id = :user", user=session["user_id"])   
                
                input_username = rowss[0]["username"]
                
                """Recording transaction into new table (transactions)"""
                
                db.execute("INSERT INTO transactions (id, username, stock, price, shares, total_spent) VALUES (:user, :username, :stock, :price, :shares, :total_spent)",
                user=session["user_id"], username=session["username"], stock=request.form.get("symbol"),
                price=price, shares=(request.form.get("shares")), total_spent=total) 
                """ price, shares, total_spent, date"""
                
                
                """Updating wallet balance"""
                
                newtotal = wallet - total
                db.execute("UPDATE users SET cash = :newtotal  WHERE id = :user", newtotal=newtotal, user=session["user_id"])
                """Showing main page"""     
                
                # Update history table
                db.execute("INSERT INTO history(id, stock, shares, price) VALUES (:user, :symbol, :amount, :value)",
                user=session["user_id"], symbol=request.form.get("symbol"), amount=(request.form.get("shares")), value=price)
                
                return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # query database with the transactions history
    rows = db.execute("SELECT stock, shares, price, timestamp FROM history WHERE id = :user",
                            user=session["user_id"])

    # pass a list of lists to the template page, template is going to iterate it to extract the data into a table
    transactions = []
    for row in rows:
        stock_info = lookup(row['stock'])
        row['price'] = '$'+str(row['price'])
        

        # create a list with all the info about the transaction and append it to a list of every stock transaction
        transactions.append(list((stock_info['symbol'], stock_info['name'], row['shares'], row['price'], row['timestamp'])))
    
    # redirect user to index page
    return render_template("history.html", transactions=transactions)

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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        
        #Remember the name from the user logged in
        session["username"] = rows[0]["username"]

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
        return render_template("quote.html")
    else:
        if not lookup(request.form.get("symbol")):
            return apology("Sorry this stock doesn't exist")
            
        else:
            stock_data = lookup(request.form.get("symbol"))
            stock_name = stock_data["name"]
            stock_symbol = stock_data["symbol"]
            stock_price = stock_data["price"]
            return render_template("quoted.html", stock_name = stock_name, stock_symbol = stock_symbol, stock_price = stock_price)
    

@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "POST":
        
        #Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
            
        # Ensure password was repeated
        elif not request.form.get("repeat_password"):
            return apology("must repeat password", 403)

            """Check if username already exists"""
            username = request.form.get("username")
            
        if db.execute("SELECT * FROM users WHERE username = :username",
            username=request.form.get("username")):
            return render_template("repeated_username.html")
                
        else:
            """Check if password matches"""
            password = request.form.get("password")
            repeat_password = request.form.get("repeat_password")
                
            if password != repeat_password:
                return render_template("password_nomatch.html")
                    
            else:
                    
                """Run hash on the password before storing it"""
                salt = os.urandom(32) # Remember this
    
                db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username") , 
                hash = generate_password_hash(request.form.get("password")))
                return redirect("/")
                
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    
    if request.method == "GET":
        # query database with the transactions history
        rows = db.execute("SELECT stock, shares FROM transactions WHERE id = :user",
        user=session["user_id"])
    
        # create a dictionary with the availability of the stocks
        stocks = {}
        for row in rows:
            stocks[row['stock']] = row['shares']
    
        return render_template("sell.html", stocks=stocks)
    
    if request.method == "POST":
        # collect relevant informations
        amount=int(request.form.get("amount"))
        symbol=request.form.get("symbol")
        price=lookup(symbol)["price"]
        value=round(price*float(amount))
    
        # Update stocks table
        amount_before = db.execute("SELECT shares FROM transactions WHERE id = :user AND stock = :symbol",
        symbol=symbol, user=session["user_id"])[0]['shares']
        amount_after = amount_before - amount
        
        
    
        # delete stock from table if we sold every unit we had
        if amount_after == 0:
            db.execute("DELETE FROM transactions WHERE id = :user AND stock = :symbol",
            symbol=symbol, user=session["user_id"])
            return redirect("/")
    
        # stop the transaction if the user does not have enough stocks
        elif amount_after < 0:
            return apology("That's more than the stocks you own")
            
        else:
            db.execute("UPDATE transactions SET shares = :shares WHERE id = :user AND stock = :symbol",
                          symbol=symbol, user=session["user_id"], shares=amount_after)
                          
                    # calculate and update user's cash
            cash = db.execute("SELECT cash FROM users WHERE id = :user",
                              user=session["user_id"])[0]['cash']
            cash_after = cash + price * float(amount)
    
            db.execute("UPDATE users SET cash = :cash WHERE id = :user",
                              cash=cash_after, user=session["user_id"])
    
            # Update history table
            db.execute("INSERT INTO history(id, stock, shares, price) VALUES (:user, :symbol, :amount, :value)",
                    user=session["user_id"], symbol=symbol, amount=-amount, value=price)
    
            # Redirect user to home page with success message
            flash("Sold!")
            return redirect("/")
    
@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit(): 
    
    if request.method == "GET":
        return render_template("deposit.html")
    
    if request.method == "POST":
        
        """Calculate user current cash"""
        cash_calc = db.execute("SELECT cash FROM users WHERE id = :user",
        user=session["user_id"])[0]['cash']
        cash_calc_after = cash_calc + float(request.form.get("amount"))
        amount=int(request.form.get("amount"))

        db.execute("UPDATE users SET cash = :cash WHERE id = :user",
        cash=cash_calc_after, user=session["user_id"])
                              
        flash(f"You successfully added ${amount} to your account!")
        return redirect("/")
        

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
