from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import hashlib
import locale
import json
import random

#Creating an app usinng flask
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


#rendering the landing or the home page
@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0")
