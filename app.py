from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import hashlib
import locale
import json
import random
from datetime import datetime

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
        return render_template("error.html",error_title="Rendering Error!", error_message="Network or some internal error occurred while rendering the page.")


#signup route
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    try:
        if request.method == 'POST':
            con=connect_db()
            cursor=con.cursor()
            first_name = request.form.get('fname')
            last_name = request.form.get('lname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            length=len(phone)
            dob = request.form.get('dd')
            blood_group = request.form.get('bgroup')
            password = request.form.get('pword')

            # Check if email or phone number already exists
            cursor.execute('SELECT COUNT(*) FROM userdetails WHERE email = ? OR phonenumber = ?', (email, phone))
            existing_count = cursor.fetchone()[0]

            if existing_count > 0:
                # Checking  Email or phone number already exists!
                return render_template("error.html", error_title="Please use a different one.",error_message="Email or phone number already exists!")
            if(length!=10):
                #Checking valid phone number or not
                return render_template("error.html", error_title="Invalid Number!",error_message="phone number you entered is not an valid number!")
            # Calculate age based on the provided date of birth
            dob_date = datetime.strptime(dob, '%Y-%m-%d')
            today = datetime.now()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
            print(age)
            
            # Check if the age is within the specified range
            if age < 18 or age >= 65:
                # Age is not within the allowed range, display an error message
                return render_template("error.html", error_message="Age must be between 18 and 64 years old.")

            cursor.execute('SELECT COUNT(*) FROM userdetails')  
            count = cursor.fetchone()[0]
            count=count+1
            #formating the user given deatils for eazy storage
            name=first_name + " " + last_name

            #Updating the user details into the database
            
            cursor.execute("INSERT INTO userdetails (id,name,email,phonenumber,bloodgroup,dob,password) VALUES (?, ?, ?, ?, ?, ?, ?)", (count,name,email,phone,blood_group,dob,password))
            con.commit()
            con.close()

            # Store username in session
            session['username'] = name

            return render_template("index.html", current_user=name)
        return render_template("getstarted.html")
    except:
        title="Signup Error!@#$"
        message="Error updating the database with your details for signup!."
        return render_template("error.html",error_title=title,error_message=message)


#login page
@app.route('/login', methods=['POST', 'GET'])
def login():
    try:
        if 'username' in session:
            # If user is already logged in, redirect to index
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            con = connect_db()
            cursor = con.cursor()

            # Check if the email and password match
            cursor.execute('SELECT name FROM userdetails WHERE email = ? AND password = ?', (email, password))
            user = cursor.fetchone()

            if user:
                # If credentials match, set the username in the session
                session['username'] = user[0]
                con.close()
                return render_template("index.html", current_user=user[0])

            con.close()
            # If credentials don't match, you can render an error message or redirect to the login page
            return render_template("error.html", error_message="Invalid email or password.")

        return render_template("login.html")
    except:
        return render_template("error.html", error_message="Unexpected error while logging in",error_title="Login error!")
# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0")
