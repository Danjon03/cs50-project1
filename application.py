import os
import requests
from flask import Flask, render_template, jsonify, request
from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = 'any random string'
# Check for environment variable
#if not os.getenv("postgres://hfoyscerojovrt:9aa6db37bf6c99bc5b806ba8e679951e387bac50c354ad7130b87008d2610fb5@ec2-23-21-115-109.compute-1.amazonaws.com:5432/de22mq4gjusq1k"):
    #raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://yrvbdnsfuhceho:40cb439d797a2b91367eef8bd315625e200345bbcf75307c41cd100cc400655d@ec2-54-204-37-92.compute-1.amazonaws.com:5432/d8rm504f5lp50s")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/logout")
def logout():
	session.pop("username", None)
	users = db.execute("SELECT * FROM users").fetchall()
	return render_template("index.html")

@app.route("/")
def index():
	print("start")
	users = db.execute("SELECT * FROM users").fetchall()
	if 'username' in session:
		return render_template("main.html")
	else:
		return render_template("index.html", users=users)


@app.route("/submitForm/<books_isbn>", methods=["POST"])
def submitForm(books_isbn):
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "jJStrByB2LZcEbVtFciMQ", "isbns": books_isbn})
	review = request.form.get("reviewBox")
	stars = request.form.get("hello")
	books = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": books_isbn}).fetchone()
	reviews = db.execute("SELECT username, reviews, starrating FROM userinput WHERE isbn = :isbn", {"isbn": books_isbn}).fetchall()
	if db.execute("SELECT username FROM userinput WHERE isbn = :isbn;", {"isbn": books_isbn}).rowcount == 0:
		db.execute("INSERT INTO userinput (username, reviews, isbn, starrating) VALUES(:username, :reviews, :isbn, :stars);", 
		{"username": session["username"], "reviews": review, "isbn": books_isbn, "stars": stars})
		db.commit()
		
		return render_template("bookInfo.html", books=books, reviews=reviews, res=res)
	else:
		return render_template("bookInfo.html", books=books, reviews=reviews, message="You can only make one review per book", res=res)
	
	
	

@app.route("/bookInfo/<book_isbn>")
def bookInfo(book_isbn):
	
	
	
	
	resNew = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "jJStrByB2LZcEbVtFciMQ", "isbns": book_isbn}).json()["books"][0]
	
	rating_count = resNew["ratings_count"]
	average_rating = resNew["average_rating"]
	books = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
	reviews = db.execute("SELECT username, reviews FROM userinput WHERE isbn = :isbn", {"isbn": book_isbn}).fetchall()
	
	return render_template("bookInfo.html", books=books, reviews=reviews, rating_count=rating_count, average_rating=average_rating)
	
	
	


@app.route("/search", methods=["POST"])
def search():
	
	
	s = request.form.get("search")
	books = db.execute("SELECT * FROM books WHERE title = :s OR author = :s OR isbn = :s;", {"s": s})
	return render_template("searchResults.html", books=books)
	


#when create an account is pressed this happens
@app.route("/create", methods=["POST"])
def create():


	# Get form information.
	username = request.form.get("username")
	password = request.form.get("password")

	
	# find if the username and password already exists
	
	if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 1:
	
		return render_template("error.html", message="Someone already has that username. Press back to try again.")
		
	else:
		db.execute("INSERT INTO users (username, password) VALUES(:Username, :Password)", {"Username": username, "Password": password})
		db.commit()
		return render_template("main.html")
		
@app.route("/login", methods=["POST"])
def login():
	u = request.form.get("username")
	p = request.form.get("password")

	if db.execute("SELECT * FROM users WHERE username = :Username AND password = :Password;", {"Username": u, "Password": p}).rowcount == 0:
		
		
		return render_template("error.html", message=f"Your username and pasword do not match")
	else:
		session["username"] = u
		return render_template("main.html")

@app.route("/api/books/<isbn>")
def book_api(isbn):
	requestedBook = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn})
	if requestedBook is None:
		return jsonify({"error": "Invalid isbn"}), 422
	else:
		return jsonify({

			"title": requestedBook.title,
			"Author": requestedBook.author,
			"Year": requestedBook.year,
			"ISBN": requestedBook.isbn})

#good reads key jJStrByB2LZcEbVtFciMQ

if __name__ == '__main__':
	
	index()