from cs50 import SQL
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
# Create a temporary file to store sessions
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Create session object by passing in application
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///booknotes.db")

# Flask function that runs on each page inside the app to require the user to be logged in
# If not logged in, returns the /login page
def login_required(f):

    # Decorate routes to require login (https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/)
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If the user is not logged in, redirect them to login page
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# / ROUTE
@app.route("/")
@login_required
def index():
        return render_template("index.html")

# /REGISTRATION ROUTE
@app.route("/registration", methods=["GET", "POST"])
def registration():
        if request.method == "GET":
                return render_template("registration.html")

        if request.method == "POST":
                # Get username, password, and password confirmation from form sumbitted
                username = request.form.get("username")
                password = request.form.get("password")
                confirmation = request.form.get("confirmation")

                # If username/password/password confirmation is blank, return error
                if not username or not password or not confirmation:
                        error_message = "Required fields cannot be empty. Please enter a username, password, and password confirmation."
                        return render_template("registration-error.html", error_message = error_message)

                # If passwords don't match, return error
                elif password != confirmation:
                        error_message = "The passwords you entered do not match. Please try again."
                        return render_template("registration-error.html", error_message = error_message)

                # Generate hash password
                hash = generate_password_hash(password)

                # Register user in database
                try:
                        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

                # If the username already exists, return error
                except:
                        error_message = "This account name already exists. Login "
                        link = "/login"
                        linked_text = "here"
                        error_message_cont = "."
                        return render_template("registration-error.html", error_message = error_message, link = link, linked_text = linked_text, error_message_cont = error_message_cont)

                # Start a user session - select user's row from the user table
                rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

                # Find their session id and start a session
                session["user_id"] = rows[0]["id"]

                # Return to home page
                return redirect("/")

# /LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():

        # Forget any user_id
        session.clear()

        if request.method == "POST":

                # Ensure username and password fields are not empty
                if not request.form.get("username") or not request.form.get("password"):

                        # If username/password field is empty, return error
                        error_message = "Required fields cannot be empty. Please enter a username and a password."
                        return render_template("login-error.html", error_message = error_message)

                # Query database for username (should return 1 row)
                rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

                # Ensure username exists (if there was not 1 row returned above, return error)
                if len(rows) != 1:

                        # If username does not exist, return error
                        link = "/registration"
                        linked_text = "here"
                        error_message_cont = "."
                        error_message = "The username you entered does not exist. Please enter a valid username, or register for a new account"
                        return render_template("login-error.html", link = link, linked_text = linked_text, error_message = error_message, error_message_cont = error_message_cont)

                # Ensure password is correct (if password entered does not match the password in database from the row returned above in "rows")
                elif not check_password_hash(rows[0]["hash"], request.form.get("password")):

                        # If the password is wrong, return error
                        error_message = "The password you entered is incorrect. Please try again."
                        return render_template("login-error.html", error_message = error_message)

                # If login credentials are valid, log the user in
                else:

                        # Remember which user has logged in
                        session["user_id"] = rows[0]["id"]

                        # Redirect user to home page
                        return redirect("/")

        if request.method == "GET":
                return render_template("login.html")

# /LOGOUT ROUTE
@app.route("/logout")
def logout():

        # Forget any user_id (log user out)
        session.clear()

        # Redirect user to login screen
        return redirect("/login")

# /NEW-BOOK ROUTE
@app.route("/new-book", methods=["GET", "POST"])
@login_required
def newbook():

        # If user enters a new book entry, enter the book in the database table "books"
        if request.method == "POST":
               current_user_id = session["user_id"]
               new_book_title = request.form.get("addbook")

               # Variable to send to "/add-first-entry" route, to get book title
               session['my_var'] = new_book_title

               # Error checking - check if the book title entered already exists
               if not db.execute ("SELECT * FROM books WHERE user_id = ? AND book_title = ?", current_user_id, new_book_title):

                        # If the book does not already exist, SQL statement to enter the new book in the "books" table, entered as (not completed), and (not on wishlist)
                        db.execute("INSERT INTO books (user_id, book_title, completed, wishlist) VALUES (?, ?, ?, ?)",
                        current_user_id, new_book_title, "N", "N")

               # If the book already exists, return error
               else:

                       # Find out if the book exists under "Currently Reading" or under "Wishlist"
                       # Assume it exists under "Currently Reading" - location variable will be changed via the statements below if it exists elsewhere
                       location = "Currently Reading"
                       link_location = "/currently-reading"

                       # If the book has 'Y' under "wishlist", then it is on the wishlist - update the location variable value to "Want to Read" (the user's wishlist)
                       if db.execute ("SELECT * FROM books WHERE user_id = ? AND book_title = ? AND wishlist = 'Y'" , current_user_id, new_book_title):
                                location = "Want to Read"
                                link_location = "/want-to-read"

                       # If the book is not on the wishlist, also check if the user has already completed the book - if so, update the location variable to "Completed"
                       # If the book has 'Y' under "completed", then it has been completed
                       elif db.execute ("SELECT * FROM books WHERE user_id = ? AND book_title = ? AND completed = 'Y'" , current_user_id, new_book_title):
                                location = "Completed"
                                link_location = "/completed"

                       # Return error message, and let the user know where the book exists (under currently reading, want to read, or completed)
                       error_message = "The book title you entered already exists under  " + location + ". Please use "
                       # Offer the user re-direction to where the book already exists
                       link = link_location
                       linked_text = location
                       error_message_cont = "to make any updates to this book, or enter a different book title."
                       return render_template("new-book-error.html", error_message = error_message, link = link, linked_text = linked_text, error_message_cont = error_message_cont)

               # Query for newly entered book, and render the title on the add-first-entry template
               book = db.execute("SELECT * FROM books WHERE user_id = ? AND book_title = ?", current_user_id, new_book_title)
               return render_template("add-first-entry.html", book=book)

        if request.method == "GET":
                return render_template("new-book.html")

# /CURRENTLY-READING ROUTE
@app.route("/currently-reading", methods=["GET", "POST"])
@login_required
def currentlyreading():
        if request.method == "GET":
                current_user_id = session["user_id"]

                # Query for all current books the current user is currently reading, to create a drop-down menu with these book options
                books = books = db.execute("SELECT * FROM books WHERE user_id = ? AND completed = 'N' AND wishlist = 'N'", current_user_id)
                return render_template("currently-reading.html", books=books)

        if request.method == "POST":

                current_user_id = session["user_id"]
                current_book_title = request.form.get("book")
                current_book_id = db.execute("SELECT id FROM books WHERE book_title = ?", current_book_title)
                notes = db.execute("SELECT * FROM notes WHERE user_id = ? AND book_id = ?", current_user_id, current_book_id[0]["id"])

                # Render the notes template with the note entries for the book the user has selected and submitted
                return render_template("notes.html", booktitle=current_book_title, notes=notes)

# /ADD-FIRST-ENTRY ROUTE
@app.route("/add-first-entry", methods=["GET", "POST"])
@login_required
def addfirstentry():

        # If user enters a new book entry, enter the book in the database table "books"
        if request.method == "POST":

               current_user_id = session["user_id"]
               notes_entry = request.form.get("addfirstentry")
               entry_date = datetime.now()

               # Convert time from UTC to EST
               hour = entry_date.strftime("%H")

               if hour == "00":
                converted_hour = "20"

               elif hour == "01":
                converted_hour = "21"

               elif hour == "02":
                converted_hour = "22"

               elif hour == "03":
                converted_hour = "23"

               else:
                converted_hour = str(int(hour) - 4)

                # Add additional "0" to time format if time is between 0-9 to always have two digits for the hour value
                if int(converted_hour) <= 9:
                        converted_hour = "0" + converted_hour

               # Format the date (https://www.w3schools.com/python/python_datetime.asp)
               date = (entry_date.strftime("%a") + " " + entry_date.strftime("%b") + " " + entry_date.strftime("%d") + " " + entry_date.strftime("%G") + " " + converted_hour + ":" + entry_date.strftime("%M") + " EST")

               # Carrying variable over from "/new-book" or "/start-book" route, to get book title
               current_book_title = session.get('my_var', None)
               current_book_id = db.execute("SELECT id FROM books WHERE book_title = ?", current_book_title)

               # SQL statement to enter the new notes entry to newly started book
               db.execute("INSERT INTO notes (user_id, book_id, date, notes) VALUES (?, ?, ?, ?)",
               current_user_id, current_book_id[0]["id"], date, notes_entry)

               notes = db.execute("SELECT * FROM notes WHERE user_id = ? AND book_id = ?", current_user_id, current_book_id[0]["id"])
               success_message = "Success! Your entry has been successfully entered!"
               return render_template("notes-success.html", booktitle=current_book_title, notes=notes, success_message=success_message)

        if request.method == "GET":
                return render_template("add-first-entry.html")

# /NOTES ROUTE
@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
         return render_template("notes.html")

# /ADD-ENTRY ROUTE
@app.route("/add-entry", methods=["GET", "POST"])
@login_required
def addentry():
        if request.method == "GET":
                current_user_id = session["user_id"]

                # Query for all current books the current user is reading, to create a drop-down menu with these book options
                books = books = db.execute("SELECT * FROM books WHERE user_id = ? AND completed = 'N' AND wishlist = 'N'", current_user_id)
                return render_template("add-entry.html", books=books)

        if request.method == "POST":

                current_user_id = session["user_id"]
                current_book_title = request.form.get("book")
                current_book_id = db.execute("SELECT id FROM books WHERE book_title = ?", current_book_title)
                entry_date = datetime.now()

                # Convert UTC to EST
                hour = entry_date.strftime("%H")

                if hour == "00":
                 converted_hour = "20"

                elif hour == "01":
                 converted_hour = "21"

                elif hour == "02":
                 converted_hour = "22"

                elif hour == "03":
                 converted_hour = "23"

                else:
                 converted_hour = str(int(hour) - 4)

                # Add additional "0" to time format if time is between 0-9 to always have two digits for the hour value
                if int(converted_hour) <= 9:
                        converted_hour = "0" + converted_hour

                # Format the date (https://www.w3schools.com/python/python_datetime.asp)
                date = (entry_date.strftime("%a") + " " + entry_date.strftime("%b") + " " + entry_date.strftime("%d") + " " + entry_date.strftime("%G") + " " + converted_hour + ":" + entry_date.strftime("%M") + " EST")

                notes_entry = request.form.get("addentry")

                db.execute("INSERT INTO notes (user_id, book_id, date, notes) VALUES (?, ?, ?, ?)",
                current_user_id, current_book_id[0]["id"], date, notes_entry)

                # Query for notes to be rendered on the notes template when form is submitted
                notes = db.execute("SELECT * FROM notes WHERE user_id = ? AND book_id = ?", current_user_id, current_book_id[0]["id"])
                success_message = "Success! Your entry has been successfully entered!"
                return render_template("notes-success.html", booktitle=current_book_title, notes=notes, success_message=success_message)

# /COMPLETE-BOOK ROUTE
@app.route("/complete-book", methods=["GET", "POST"])
@login_required
def completebook():
        if request.method == "GET":
                current_user_id = session["user_id"]

                # Query for all current books the current user is reading, to create a drop-down menu with these book options
                books = books = db.execute("SELECT * FROM books WHERE user_id = ? AND completed = 'N' AND wishlist = 'N'", current_user_id)
                return render_template("complete-book.html", books=books)

        if request.method == "POST":
                current_user_id = session["user_id"]
                current_book_title = request.form.get("book")

                # Change completed book status from N to Y
                db.execute("UPDATE books SET completed = 'Y' WHERE book_title = ?", current_book_title)
                success_message = "Success! Your book has been successfully moved to Completed!"
                return render_template("index-success.html", success_message=success_message)

# /DELETE-BOOK ROUTE
@app.route("/delete-book", methods=["GET", "POST"])
@login_required
def deletebook():
        if request.method == "GET":
                current_user_id = session["user_id"]

                # Query for all current books the current user is reading, to create a drop-down menu with these book options
                books = books = db.execute("SELECT * FROM books WHERE user_id = ? AND completed = 'N' AND wishlist = 'N'", current_user_id)
                return render_template("delete-book.html", books=books)

        if request.method == "POST":
                current_user_id = session["user_id"]
                current_book_title = request.form.get("book")
                current_book_id = db.execute("SELECT id FROM books WHERE book_title = ?", current_book_title)

                # Delete any notes associated with deleted book
                db.execute("DELETE FROM notes WHERE book_id = ?", current_book_id[0]["id"])

                # Delete book that the user has selected
                db.execute("DELETE FROM books WHERE book_title = ?", current_book_title)

                # Query for all remaining current books the current user is reading, to create a drop-down menu with these book options
                books = books = db.execute("SELECT * FROM books WHERE user_id = ? AND completed = 'N' AND wishlist = 'N'", current_user_id)
                success_message = "Success! Your book has been successfully deleted!"
                return render_template("currently-reading-success.html", books=books, success_message=success_message)

# /COMPLETED ROUTE
@app.route("/completed", methods=["GET", "POST"])
@login_required
def completed():
        if request.method == "GET":
                current_user_id = session["user_id"]

                # Query for all books the current user has completed, to create a drop-down menu with these book options
                books = books = db.execute("SELECT * FROM books WHERE user_id = ? AND completed = 'Y'", current_user_id)
                return render_template("completed.html", books=books)

        if request.method == "POST":
                current_user_id = session["user_id"]
                current_book_title = request.form.get("book")

                # Query for the notes from selected book, and return them in the notes template
                current_book_id = db.execute("SELECT id FROM books WHERE book_title = ?", current_book_title)
                notes = db.execute("SELECT * FROM notes WHERE user_id = ? AND book_id = ?", current_user_id, current_book_id[0]["id"])
                return render_template("notes.html", booktitle=current_book_title, notes=notes)

# /REVERT-BOOK ROUTE
@app.route("/revert-book", methods=["GET", "POST"])
@login_required
def revertbook():
        if request.method == "GET":
                current_user_id = session["user_id"]

                # Query for all current books the current user has completed, to create a drop-down menu with these book options
                books = books = db.execute("SELECT * FROM books WHERE user_id = ? AND completed = 'Y'", current_user_id)
                return render_template("revert-book.html", books=books)

        if request.method == "POST":
                current_user_id = session["user_id"]
                current_book_title = request.form.get("book")

                # Change completed book status from Y to N
                db.execute("UPDATE books SET completed = 'N' WHERE book_title = ?", current_book_title)
                success_message = "Success! Your book has been successfully reverted to Currently Reading!"
                return render_template("index-success.html", success_message=success_message)

# /DELETE-BOOK-COMPLETED ROUTE
@app.route("/delete-book-completed", methods=["GET", "POST"])
@login_required
def deletebookcompleted():
        if request.method == "GET":
                current_user_id = session["user_id"]

                # Query for all current books the current user has completed, to create a drop-down menu with these book options
                books = books = db.execute("SELECT * FROM books WHERE user_id = ? AND completed = 'Y'", current_user_id)
                return render_template("delete-book-completed.html", books=books)

        if request.method == "POST":
                current_user_id = session["user_id"]

                # Delete any notes associated with deleted book
                current_book_title = request.form.get("book")
                current_book_id = db.execute("SELECT id FROM books WHERE book_title = ?", current_book_title)
                db.execute("DELETE FROM notes WHERE book_id = ?", current_book_id[0]["id"])

                # Delete book that the user has selected
                db.execute("DELETE FROM books WHERE book_title = ?", current_book_title)

                # Query for all remaining books the current user has completed, to create a drop-down menu with these book options
                current_user_id = session["user_id"]
                books = books = db.execute("SELECT * FROM books WHERE user_id = ? AND completed = 'Y'", current_user_id)
                success_message = "Success! Your book has been successfully deleted!"
                return render_template("completed-success.html", books=books, success_message=success_message)

# /WANT-TO-READ ROUTE
@app.route("/want-to-read")
@login_required
def wanttoread():
        current_user_id = session["user_id"]

        # Query for all books on current user's wishlist, to create a drop-down menu with these book options
        books = db.execute("SELECT * FROM books WHERE user_id = ? AND wishlist = 'Y'", current_user_id)
        return render_template("want-to-read.html", books=books)

# /ADD-BOOK ROUTE
@app.route("/add-book", methods=["GET", "POST"])
@login_required
def addbook():

        # If user enters a new book to list, enter the book in the database table "books", with "wishlist" as Y
        if request.method == "POST":
               current_user_id = session["user_id"]
               new_book_title = request.form.get("addbookreadinglist")

               # Error checking - check if the book title entered by user already exists
               if not db.execute ("SELECT * FROM books WHERE user_id = ? AND book_title = ?", current_user_id, new_book_title):

                        # SQL statement to enter the new book in the "books" table, entered as (not completed), and (on wishlist)
                        db.execute("INSERT INTO books (user_id, book_title, completed, wishlist) VALUES (?, ?, ?, ?)",
                        current_user_id, new_book_title, "N", "Y")

               # If the book already exists, return error
               else:

                       # Find out if the book exists under "Currently Reading" or under "Completed"
                       # Assume it exists under "Currently Reading" - location variable will be changed via the statements below if it exists elsewhere
                       location = "Currently Reading"
                       link_location = "/currently-reading"

                     # If the book has 'Y' under "wishlist", then it is on the wishlist - update the location variable value to "Want to Read" (the user's wishlist)
                       if db.execute ("SELECT * FROM books WHERE user_id = ? AND book_title = ? AND wishlist = 'Y'" , current_user_id, new_book_title):
                                location = "Want to Read"
                                link_location = "/want-to-read"

                       # If the book is not on the wishlist, also check if the user has already completed the book. If so, update the location variable to "Completed".
                       # If the book has 'Y' under "completed", then it has been completed
                       elif db.execute ("SELECT * FROM books WHERE user_id = ? AND book_title = ? AND completed = 'Y'" , current_user_id, new_book_title):
                                location = "Completed"
                                link_location = "/completed"

                       # Return error message, and let the user know where the book exists (under currently reading or want to read)
                       error_message = "The book title you entered already exists under  " + location + ". Please use "
                       # Offer the user re-direction where the book already exists
                       link = link_location
                       linked_text = location
                       error_message_cont = "to make any updates to this book, or enter a different book title."
                       return render_template("add-book-error.html", error_message = error_message, link = link, linked_text = linked_text, error_message_cont = error_message_cont)

               # Query for all books on current user's wishlist, to create a drop-down menu with these book options, and return the list using the want-to-read template
               current_user_id = session["user_id"]
               books = db.execute("SELECT * FROM books WHERE user_id = ? AND wishlist = 'Y'", current_user_id)
               success_message = "Success! Your book has been successfully added to your wishlist!"
               return render_template("want-to-read-success.html", books=books, success_message=success_message)

        if request.method == "GET":
                return render_template("add-book.html")

# /START-BOOK ROUTE
@app.route("/start-book", methods=["GET", "POST"])
@login_required
def startbook():

        if request.method == "GET":
                current_user_id = session["user_id"]

                # Query for all books on reading list, to create a drop-down menu with these book options
                books = books = db.execute("SELECT * FROM books WHERE user_id = ? AND wishlist = 'Y'", current_user_id)
                return render_template("start-book.html", books=books)

        # If user chooses a book to start reading, change "wishlist" from Y to N, and re-direct to /add-first-entry route
        if request.method == "POST":
               current_user_id = session["user_id"]
               book_to_start = request.form.get("book")

               # Variable to send to "add-first-entry" route, to get book title
               session['my_var'] = book_to_start

               # SQL statement to change "wishlist from Y to N
               db.execute("UPDATE books SET wishlist = 'N' WHERE book_title = ?", book_to_start)

               # Query for newly started book, and render on the add-first-entry template
               book = db.execute("SELECT * FROM books WHERE user_id = ? AND book_title = ?", current_user_id, book_to_start)
               return render_template("add-first-entry.html", book=book)

# /DELETE-BOOK-READING-LIST ROUTE
@app.route("/delete-book-reading-list", methods=["GET", "POST"])
@login_required
def deletebookreadinglist():
        if request.method == "GET":
                current_user_id = session["user_id"]

                # Query for all books on reading list, to create a drop-down menu with these book options
                books = books = db.execute("SELECT * FROM books WHERE user_id = ? AND wishlist = 'Y'", current_user_id)
                return render_template("delete-book-reading-list.html", books=books)

        if request.method == "POST":
                current_user_id = session["user_id"]

                # Delete any notes associated with deleted book
                current_book_title = request.form.get("book")
                current_book_id = db.execute("SELECT id FROM books WHERE book_title = ?", current_book_title)
                db.execute("DELETE FROM notes WHERE book_id = ?", current_book_id[0]["id"])

                # Delete book that the user has selected
                db.execute("DELETE FROM books WHERE book_title = ?", current_book_title)

                # Query for all remaining books on current user's wishlist, to create a drop-down menu with these book options, and return the list using the want-to-read template
                books = db.execute("SELECT * FROM books WHERE user_id = ? AND wishlist = 'Y'", current_user_id)
                success_message = "Success! Your book has been successfully deleted!"
                return render_template("want-to-read-success.html", books=books, success_message=success_message)