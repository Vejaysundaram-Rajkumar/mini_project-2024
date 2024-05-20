from flask import Flask,jsonify, render_template, request, redirect, session, url_for
import sqlite3
import hashlib
import locale
import json
import random
import time
from datetime import datetime
import main
import smtplib
from email.mime.text import MIMEText
#Creating an app usinng flask
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#Connect with the database to store the user details
def connect_db():
    connection = sqlite3.connect('userdatabase.db')
    return connection
# Function to generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Function to send OTP via email
def send_email(email, otp):
    sender_email = "bloodline.at.2024@gmail.com"  # Enter your email
    sender_password = "loxqrxxrrlnlufqy"       # Enter your password

    message = MIMEText(f"Your OTP for email verification is: {otp}")

    message['Subject'] = 'Email Verification OTP'
    message['From'] = sender_email
    message['To'] = email

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, [email], message.as_string())
    server.quit()

#signup route
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    try:
        if request.method == 'POST':
            con = connect_db()
            cursor = con.cursor()
            first_name = request.form.get('fname')
            last_name = request.form.get('lname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            length = len(phone)
            dob = request.form.get('dd')
            blood_group = request.form.get('bgroup')
            password = request.form.get('pword')

            # Check if email or phone number already exists
            cursor.execute('SELECT COUNT(*) FROM userdetails WHERE email = ? OR phonenumber = ?', (email, phone))
            existing_count = cursor.fetchone()[0]

            if existing_count > 0:
                # Checking Email or phone number already exists!
                return render_template("error.html", error_title="Please use a different one.",
                                       error_message="Email or phone number already exists!")
            if length != 10:
                # Checking valid phone number or not
                return render_template("error.html", error_title="Invalid Number!",
                                       error_message="phone number you entered is not an valid number!")

            # Calculate age based on the provided date of birth
            dob_date = datetime.strptime(dob, '%Y-%m-%d')
            today = datetime.now()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))

            # Check if the age is within the specified range
            if age < 18 or age >= 65:
                # Age is not within the allowed range, display an error message
                return render_template("error.html", error_message="Age must be between 18 and 64 years old.")

            cursor.execute('SELECT COUNT(*) FROM userdetails')
            count = cursor.fetchone()[0]
            count = count + 1
            # formating the user given deatils for eazy storage
            name = first_name + " " + last_name

            # Store user details in session
            session['user_details'] = {
                'name': name,
                'email': email,
                'phone': phone,
                'dob': dob,
                'blood_group': blood_group,
                'password': password
            }

            # Generate OTP and store in session
            otp = generate_otp()
            session['otp'] = otp

            # Send OTP via email
            send_email(email, otp)

            # Redirect to email verification page
            return render_template("verification.html")

        return render_template("getstarted.html")
    except Exception as e:
        # Handle exceptions
        return render_template("error.html", error_title="Signup Error!", error_message=str(e))

# Email verification route
@app.route('/verify', methods=['GET', 'POST'])
def verify_email():
    try:
        if request.method == 'POST':
            otp_entered = request.json.get('otp')
            if otp_entered == session.get('otp'):
                # Account verified, proceed with account creation
                user_details = session.get('user_details')
                name = user_details['name']
                email = user_details['email']
                phone = user_details['phone']
                dob = user_details['dob']
                blood_group = user_details['blood_group']
                password = user_details['password']

                con = connect_db()
                cursor = con.cursor()
                cursor.execute('SELECT COUNT(*) FROM userdetails')  
                count = cursor.fetchone()[0]
                count=count+1
                # Updating the user details into the database
                cursor.execute(
                    "INSERT INTO userdetails (id,name,email,phonenumber,bloodgroup,dob,password,email_verify) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (count, name, email, phone, blood_group, dob, password ,1))
                con.commit()
                con.close()

                # Clear session variables after successful signup
                session.pop('user_details')
                session.pop('otp')
                # Redirect to dashboard or any other success page
                return jsonify({'success': True})
            else:
                # Incorrect OTP entered
                return jsonify({'success': False})
    except Exception as e:
        # Handle exceptions
        return render_template("error.html", error_title="Verification Error!", error_message=str(e))

#rendering the landing or the home page
@app.route('/')
def index():
    try:
        if 'username' in session :
            username = session['username']
            return render_template("dashboard.html", current_user=username)
        else:
            return render_template("index.html")
    except:
        return render_template("error.html",error_title="Rendering Error!", error_message="Network or some internal error occurred while rendering the page.")

# Flask Route to Serve Profile Page and Handle Form Submission
@app.route('/profile')
def profile():
    try:
        if 'username' in session:
            username = session['username']
            con = connect_db()
            cursor = con.cursor()
            
            cursor.execute('SELECT * FROM userdetails WHERE name = ?', (username,))
            person_details = cursor.fetchone()  # Fetch one row containing all details

            if person_details:
                # Filter out unnecessary details (e.g., ID and password)
                filtered_details = [detail for i, detail in enumerate(person_details) if i not in [0, 6,7]]
                verification_status = "Verified" if person_details[7] == 1 else "Not Verified"
                filtered_details.append(verification_status)
                return render_template('profile.html', user_data=filtered_details)
            else:
                return render_template("error.html", error_title="User Not Found", error_message="User details not found.")
        else:
            return render_template("error.html", error_title="Not Logged In!", error_message="Profile page can be accessed only after login.")
    except Exception as e:
        # Log the exception for debugging purposes
        print(e)
        return render_template("error.html", error_title="Rendering Error!", error_message="An error occurred while rendering the page.")



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

            # Check if the email is registered
            cursor.execute('SELECT name FROM userdetails WHERE email = ?', (email,))
            registered_user = cursor.fetchone()

            if registered_user:
                # Check if the email and password match
                cursor.execute('SELECT name FROM userdetails WHERE email = ? AND password = ?', (email, password))
                user = cursor.fetchone()

                if user:
                    # If credentials match, set the username in the session
                    session['username'] = user[0]
                    con.close()
                    return render_template("dashboard.html", current_user=user[0])

                con.close()
                # If credentials don't match, you can render an error message or redirect to the login page
                return render_template("error.html", error_message="Invalid email or password.")
            return render_template("error.html", error_message="Email is not registered!")
        return render_template("login.html")
    except:
        return render_template("error.html", error_message="Unexpected error while logging in",error_title="Login error!")
# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/request_blood', methods=['POST'])
def request_blood():
    # Get requestor's location from the request
    requestor_location = request.json.get('location')
    name = session['username']
    blood_type = request.json.get('bloodType')  # Get the selected blood type
    con = connect_db()
    cursor = con.cursor()
    u1 = "SELECT * FROM userdetails WHERE name = ?"  # Replace 'table_name' with your actual table name
    va1 = (name,)
    cursor.execute(u1, va1)
    person_details = cursor.fetchone()  # Fetch one row containing all details
    
    filtered_details = [detail for i, detail in enumerate(person_details) if i not in [0,5,6, 7]]

    google_maps_link = generate_google_maps_link(requestor_location['latitude'], requestor_location['longitude'])
    
    message_1="Blood request from "+ filtered_details[0]+" for " + blood_type + "tive blood type.\n"
    ph=str(filtered_details[2])
    message_2=message_1+"\nDetails of the Requestor : \n" +"name: " + filtered_details[0] +"\nPhone number: " + ph + " \nlocation: " + google_maps_link
    if check_recent_request(filtered_details[0]):
        return jsonify({'message': 'You can make another request after 5 minutes.'}), 403
    
    cursor.execute('SELECT COUNT(*) FROM requested_details')
    count = cursor.fetchone()[0]
    count = count + 1
    timestamp = int(time.time())    
    cursor.execute('''INSERT INTO requested_details (id,requestorname, requestornumber, bloodtype, timestamp)
                    VALUES (?, ?, ?, ?, ?)''', (count, filtered_details[0], filtered_details[2],blood_type, timestamp))
    con.commit()
    con.close()  # Close the connection
    # Implement your matching algorithm to find nearby users
    other_users_no = find_other_users(filtered_details[1])
    # Notify nearby users about the blood request
    notify_nearby_users(message_2,other_users_no)
    return jsonify({'message': 'Blood request sent successfully'})
#requested_details

def generate_google_maps_link(latitude, longitude):
    return f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"


# Function to find nearby users based on location
def find_other_users(email):
    con = connect_db()
    cursor = con.cursor()
    cursor.execute("SELECT phonenumber FROM userdetails WHERE email != ?", (email,))
    phone_numbers = cursor.fetchall()
    con.close()
    # Extract phone numbers from the result set
    other_users_phone_numbers = [phone_number[0] for phone_number in phone_numbers]
    return other_users_phone_numbers

# Function to notify nearby users about the blood request
def notify_nearby_users(message_2,ph):
    for i in ph:
        i="+91"+str(i)
        print(message_2,i)
        main.request_sms(i,message_2)
        main.request_call(i,message_2)

# Function to check if a user has made a recent request within the 5-minute window
def check_recent_request(userName):
    con = connect_db()
    cursor = con.cursor()
    current_time = int(time.time())
    five_minutes_ago = current_time - (5 * 60)  # 5 minutes in seconds
    cursor.execute('''SELECT * FROM requested_details WHERE requestorname = ? AND timestamp >= ?''', (userName, five_minutes_ago))
    row = cursor.fetchone()
    con.close()
    return row is not None
if __name__ == '__main__':
    app.run(host="0.0.0.0")
