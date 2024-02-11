from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import hashlib
import locale
import json
import random

#Creating an app usinng flask
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#Connect with the database to store the user details
def connect_db():
    connection = sqlite3.connect('userdatabase.db')
    return connection

#rendering the landing or the home page
@app.route('/')
def index():
    try:
        if 'username' in session:
            username = session['username']
            return render_template("index.html", current_user=username)
        else:
            return render_template("index.html")
    except:
        return render_template("index.html")


#signin page
@app.route('/signupsubmit', methods=['POST', 'GET'])
def signupsubmit():
    try:
        if request.method == 'POST' or request.method == 'GET':
            first_name = request.form.get('fname')
            last_name = request.form.get('lname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            dd = request.form.get('dd')
            nn = request.form.get('nn')
            yyyy = request.form.get('yyyy')
            blood_group = request.form.get('bgroup')
            password = request.form.get('pword')
            name=first_name + " " + last_name
            con=connect_db()
            cursor=con.cursor()
            cursor.execute("INSERT INTO userdetails (id,name, email,phone,dd,mm,yyyy,blood_group,password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",(id,name, email,phone,dd,nn,yyyy,blood_group,password))
            con.commit()
            con.close()

            return render_template("index.html", current_user=name)
    except:
        title="Signup Error!@#$"
        message="Error updating the database with your details for signup!."
        return redirect("error.html",error_title=title,error_message=message)

#signin page
@app.route('/get-started')
def getstarted():
    return render_template("getstarted.html")

#login page
@app.route('/login')
def login():
    return render_template("login.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0")
