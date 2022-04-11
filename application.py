import os


from flask import Flask, session, render_template, request, redirect, url_for, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from users import User
from forms import SignupForm, LoginForm, BooksForm
from db.sql_run import run_sql
import controllers.userControler as userController
import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


app.secret_key = "development-key"


@app.route("/")
def index():
    if 'email' in session:
        flash(
            "Already logged in, Logout in order to switch user or register as a new user.", "danger")
        return redirect(url_for('books'))
    return render_template("index.html")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if 'email' in session:
        flash(
            "Already logged in, Logout in order to switch user or register as a new user.", "danger")
        return redirect(url_for('books'))

    form = SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit() == False:
            return render_template('signup.html', form=form)
        else:
            newUser = User(form.user_name.data,
                           form.email.data, form.password.data)
            userController.addNewUser(newUser)

            flash("Your Account has been created, you can now log in.", "success")
            return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('signup.html', form=form)


@ app.route("/login", methods=["GET", "POST"])
def login():
    if 'email' in session:
        flash("You are logged In", "danger")
        return redirect(url_for('books'))
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit() == False:
            return render_template('login.html', form=form)
        else:
            email = form.email.data
            password = form.password.data

            print(email, password)
            user = userController.getUser(email, password)
            if user is not None:
                session['email'] = form.email.data
                flash("You have been logged in succefully", "success")
                return redirect(url_for('books'))
            else:
                return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('login.html', form=form)


@ app.route("/logout")
def logout():
    session.pop('email', None)
    flash('you have logged out successfully', 'success')
    return redirect(url_for('login'))


@app.route("/books", methods=['GET', 'POST'])
def books():
    if 'email' not in session:
        flash('Please login', 'danger')
        return redirect(url_for('login'))

    form = BooksForm()
    books = db.execute("SELECT * FROM books LIMIT 30").fetchall()
    return render_template('books.html', title='Books', books=books, form=form)


@app.route("/search-page", methods=['GET', 'POST'])
def search():
    if 'email' not in session:
        flash('Please login.' 'danger')
        return redirect(url_for('login'))

    form = BooksForm()
    word = form.books.data
    if request.method == 'POST':
        if not word:
            flash("Please Enter a keyword in the search bar", "danger")
            return render_template('books.html', form=form)
        else:
            query = "SELECT * FROM books WHERE isbn LIKE '%{}%' OR author LIKE '%{}%' OR title LIKE '%{}%' ORDER BY isbn DESC LIMIT 30".format(
                word, word, word)
            results = run_sql(query)
            # print(results)
            if results:
                return render_template('search.html', books=results, form=form, word=word)
            else:
                flash("Sorry, we do not have the book you are looking for", "danger")
                return redirect(url_for('books'))
    else:
        return render_template("books.html", form=form)


@app.route("/book/<string:isbn>", methods=["GET", "POST"])
def book_details(isbn):
    if 'email' not in session:
        flash('Please login.' 'danger')
        return redirect(url_for('login'))

    user = db.execute("SELECT username FROM users WHERE lower(email) = :email", {
        'email': session['email']}).fetchone()
    book = db.execute(
        "SELECT * FROM books WHERE isbn = :book_id", {'book_id': isbn}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id",
                         {'book_id': isbn}).fetchall()

    if book is None:
        return render_template("error.html")

    response = requests.get(
        f"https://www.googleapis.com/books/v1/volumes?q={isbn}+isbn&key=AIzaSyDiFXt7Gxqc94N5_UPgf2JWhA6cNKwjaic")
    data = response.json()

    gb_rating = None
    gb_average = None
    gb_description = "Unavailable"
    if "items" in data:
        gb_rating = data['items'][0]['volumeInfo']
        gb_description = data['items'][0]['volumeInfo']['description']
        print(gb_description)
        if "ratingsCount" in gb_rating:
            gb_rating = data['items'][0]['volumeInfo']['ratingsCount']
            gb_average = data['items'][0]['volumeInfo']['averageRating']
        else:
            gb_rating = None

    already_reviewed = False
    for review in reviews:
        if review.user_id == user.username:
            already_reviewed = True
            break

    if request.method == "POST":
        comment = request.form.get("comment")
        my_rating = request.form.get("rating")
        user = db.execute("SELECT username FROM users WHERE lower(email) = :email", {
                          'email': session['email']}).fetchone()
        reviewAdd = db.execute("INSERT INTO reviews (rate, review, book_id, user_id) VALUES (:r, :c, :b, :a)", {
            "r": my_rating, "c": comment, "b": isbn, "a": user.username})
        db.commit()

        reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id",
                             {'book_id': isbn}).fetchall()

        already_reviewed = True
        return render_template("book_page.html", book_info=book, reviews=reviews, rating=gb_rating, average=gb_average, already_reviewed=already_reviewed, description=gb_description)

    if request.method == "GET":
        return render_template("book_page.html", book_info=book, reviews=reviews, rating=gb_rating, average=gb_average, already_reviewed=already_reviewed, description=gb_description)


@app.route("/api/<isbn>")
def api_get(isbn):
    if request.method == "GET":
        book = db.execute("SELECT * FROM books WHERE isbn LIKE '%{}%'".format(
            isbn)).fetchone()
        if book is None:
            return render_template("error.html", no_api=True)
    reviews = db.execute(
        "SELECT * FROM reviews WHERE book_id = :q1", {"q1": isbn}).fetchall()
    response = requests.get(
        f"https://www.googleapis.com/books/v1/volumes?q={isbn} +isbn&key=AIzaSyDiFXt7Gxqc94N5_UPgf2JWhA6cNKwjaic")
    data = response.json()

    gb_rating = None
    gb_average = None
    if "items" in data:
        gb_rating = data['items'][0]['volumeInfo']
        if "ratingsCount" in gb_rating:
            gb_rating = data['items'][0]['volumeInfo']['ratingsCount']
            gb_average = data['items'][0]['volumeInfo']['averageRating']
        else:
            gb_rating = None
    return jsonify(
        {
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "rating_count": gb_rating,
            "average_rating": gb_average
        }
    )
