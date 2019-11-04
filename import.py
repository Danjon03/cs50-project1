import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://yrvbdnsfuhceho:40cb439d797a2b91367eef8bd315625e200345bbcf75307c41cd100cc400655d@ec2-54-204-37-92.compute-1.amazonaws.com:5432/d8rm504f5lp50s")
db = scoped_session(sessionmaker(bind=engine))

def main():
    print("into main")
    f = open("books.csv")
    reader = csv.reader(f)
    print("after reader still okay!!")
    next(reader, None)
    for isbn, title, author, year in reader:
        
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
        {"isbn": isbn, "title": title, "author": author, "year": year})
        
        print(f"Added book {title}, by {author}, in {year}, isbn {isbn}")
        db.commit()

if __name__ == "__main__":
    main()
