from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
import pyrebase

# Firebase configuration
config  = {
  "apiKey": "AIzaSyCFu9G0-QWPUtGV3iONI32q4n69__jMM6E",
  "authDomain": "test-2-18803.firebaseapp.com",
  "databaseURL": "https://test-2-18803-default-rtdb.asia-southeast1.firebasedatabase.app",
  "projectId": "test-2-18803",
  "storageBucket": "test-2-18803.appspot.com",
  "messagingSenderId": "914801447775",
  "appId": "1:914801447775:web:fd28b9390557973f611cea"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
data_b = firebase.database()


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def index():
    try:
        if 'username' in session:
            username = session['username']
            return render_template("index.html", current_user=username)
        else:
            return render_template("index.html")
    except Exception as e:
        return render_template("error.html", error_title="Rendering Error!", error_message=str(e))

@app.route('/profile')
def profile():
    try:
        if 'username' in session:
            return render_template("profile.html")
        else:
            return render_template("error.html", error_title="Not Logged In!", error_message="Profile page can be accessed only after login.")
    except Exception as e:
        return render_template("error.html", error_title="Rendering Error!", error_message=str(e))

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    try:
        if request.method == 'POST':
            first_name = request.form.get('fname')
            last_name = request.form.get('lname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            dob = request.form.get('dd')
            blood_group = request.form.get('bgroup')
            password = request.form.get('pword')

            name=first_name+' '+last_name
            

            # Calculate age based on the provided date of birth
            dob_date = datetime.strptime(dob, '%Y-%m-%d')
            today = datetime.now()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))

            # Check if the age is within the specified range
            if age < 18 or age >= 65:
                return render_template("error.html", error_message="Age must be between 18 and 64 years old.")

            # Create user with email and password
            user = auth.create_user_with_email_and_password(email, password)
            
            # Store additional details in the Realtime Database
            user_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "age": age,
                "blood_group": blood_group,
                
            }
            data_b.child("users").child(user["localId"]).set(user_data)
            print("User created successfully.")

            # Set the username in the session
            session['username'] =name

            return render_template("index.html",current_user=name)

        return render_template("getstarted.html")
    except Exception as e:
        return render_template("error.html", error_title="Signup Error!@#$", error_message=str(e))

@app.route('/loginsubmit', methods=['POST', 'GET'])
def loginsubmit():
    try:
        if 'username' in session:
            return redirect(url_for('index'))

        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                userid=user['localId']
                user_name = data_b.child("users").child(userid).child('name').get().val()
                return render_template("index.html",current_user=user_name)
            except Exception as auth_error:
                # If authentication fails, render error template with the error message
                return render_template("error.html", error_message=str(auth_error))
    
    except Exception as e:
        return render_template("error.html", error_message="Unexpected error while logging in", error_title="Login error!")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            auth.send_password_reset_email(email)
            return render_template("reset_password_success.html")
        except Exception as e:
            return render_template("error.html", error_title="Password Reset Error", error_message=str(e))
    return render_template("reset_password.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0")
