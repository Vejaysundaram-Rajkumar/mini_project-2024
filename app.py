from flask import Flask, render_template, request, redirect, session, url_for
import firebase_admin
from firebase_admin import credentials, auth, db
from datetime import datetime

cred = credentials.Certificate("D:\projects\mini_project-2024\credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://testproject1-2ff78-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

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

            # Check if email already exists
            user_ref = db.reference('users')
            existing_user = user_ref.order_by_child('email').equal_to(email).get()

            if existing_user:
                return render_template("error.html", error_title="Please use a different one.", error_message="Email already exists!")

            # Calculate age based on the provided date of birth
            dob_date = datetime.strptime(dob, '%Y-%m-%d')
            today = datetime.now()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))

            # Check if the age is within the specified range
            if age < 18 or age >= 65:
                return render_template("error.html", error_message="Age must be between 18 and 64 years old.")

            # Create a new user in Firebase Authentication
            new_user = auth.create_user(
                email=email,
                password=password,
                display_name=first_name + " " + last_name
            )

            # Store additional user details in Realtime Database
            user_ref.child(new_user.uid).set({
                'name': new_user.display_name,
                'email': email,
                'phonenumber': phone,
                'bloodgroup': blood_group,
                'dob': dob
            })

            # Set the username in the session
            session['username'] = new_user.display_name

            return render_template("index.html", current_user=new_user.display_name)

        return render_template("getstarted.html")
    except Exception as e:
        return render_template("error.html", error_title="Signup Error!@#$", error_message=str(e))

@app.route('/login', methods=['POST', 'GET'])
def login():
    try:
        if 'username' in session:
            return redirect(url_for('index'))

        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            try:
                # Sign in with email and password
                user = auth.sign_in_with_email_and_password(email, password)
                session['username'] = user['displayName']
                return render_template("index.html", current_user=user['displayName'])
            except Exception as auth_error:
                return render_template("error.html", error_message=str(auth_error))

        return render_template("login.html")
    except Exception as e:
        return render_template("error.html", error_message="Unexpected error while logging in", error_title="Login error!")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0")
