import csv
import os

from flask import Flask, session, render_template, request, redirect, url_for, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(
    "postgresql://kbbwnduaoujgmy:bd8d67d7cec0fea77728e37ff3cb4b0e0593db33cbf6e578f464cdfa40df1873@ec2-18-233-83-165.compute-1.amazonaws.com:5432/ddv1olt682eu3b")
db = scoped_session(sessionmaker(bind=engine))


def addBooks():
    try:
        book = open('books.csv')
        books = csv.reader(book)
        i = 1
        for isbn, title, author, year in books:
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES(:isbn, :title, :author, :year)", {
                       'isbn': isbn, 'title': title, 'author': author, 'year': year})
            print(isbn, title, author, year)
            print(i)
            i += 1

        db.commit()
    except Exception as e:
        raise e


if __name__ == "__main__":
    addBooks()
