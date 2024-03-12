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
db = firebase.database()

def sign_up(name, email, phone, dob, blood_group, password):
    try:
        # Create user with email and password
        user = auth.create_user_with_email_and_password(email, password)
        
        # Store additional details in the Realtime Database
        user_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "dob": dob,
            "blood_group": blood_group
        }

        db.child("users").child(user["localId"]).set(user_data)
        print("User created successfully.")
    except Exception as e:
        print("Error:", e)

def sign_in(email, password):
    try:
        # Sign in with email and password
        user = auth.sign_in_with_email_and_password(email, password)
        print(user['localId'])
        print("User signed in successfully.")
        # You can now retrieve user details from the Realtime Database if needed
        return user["localId"]
    except Exception as e:
        print("Error:", e)

def fetch_user_data(user_id):
    try:
        user_data = db.child("users").child(user_id).child('email').get().val()
        print("User data:", user_data)
    except Exception as e:
        print("Error:", e)

# Example usage
if __name__ == "__main__":
    name = "John Doe"
    email = "johndoe@example.com"
    phone = "1234567890"
    dob = "1990-01-01"
    blood_group = "A+"
    password = "your_password"

    # Sign up
    sign_up(name, email, phone, dob, blood_group, password)

    # Sign in
    user_id = sign_in(email, password)

    # Fetch and print user data
    fetch_user_data(user_id)
