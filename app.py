from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, render_template_string
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from firebase_config import auth
from pymongo import MongoClient
import random, string
import os
from dotenv import load_dotenv
import pyrebase
from flask_mail import Mail, Message
import secrets  # To generate a unique reset token
import firebase_admin
from firebase_admin import credentials, auth


app = Flask(__name__)
app.secret_key = "supersecretkey"

# Load environment variables
load_dotenv()
reset_tokens = {}  # Store reset tokens temporarily

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")  # Store your MongoDB connection in .env
client = MongoClient(MONGO_URI)
db = client.url_shortener
collection = db.urls

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, uid, email):
        self.id = uid
        self.email = email

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User(user_id, "N/A")  # Dummy email since we retrieve from Firebase

# Function to generate a short ID
def generate_short_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        long_url = request.form["long_url"]
        short_id = generate_short_id()  # Function that generates a short link
        short_url = request.host_url + short_id  # Full shortened URL

        collection.insert_one({
            "user_id": current_user.id,
            "long_url": long_url,
            "short_id": short_id
        })

        return jsonify({"short_url": short_url})  # Return JSON response
    
    urls = list(collection.find({"user_id": current_user.id}))
    return render_template("dashboard.html", urls=urls)

# Redirect to the original URL
@app.route("/<short_id>")
def redirect_url(short_id):
    url_data = collection.find_one({"short_id": short_id})
    if url_data:
        return redirect(url_data["long_url"])
    return "URL not found", 404

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            auth.create_user_with_email_and_password(email, password)
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("signup"))
        except Exception as e:
            flash("Signup failed: " + str(e), "error")
            return redirect(url_for("signup"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            user_info = auth.get_account_info(user["idToken"])["users"][0]
            user_obj = User(user_info["localId"], email)
            login_user(user_obj)
            return redirect(url_for("dashboard"))
        except:
            return "Invalid credentials. Try again."
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = current_user.id
    urls = list(collection.find({"user_id": user_id}))
    return render_template("dashboard.html", urls=urls)

# DELETE route to remove a URL
@app.route("/delete/<short_id>", methods=["POST"])
@login_required
def delete_url(short_id):
    result = collection.delete_one({"user_id": current_user.id, "short_id": short_id})
    if result.deleted_count > 0:
        flash("URL deleted successfully", "success")
    else:
        flash("Failed to delete URL", "error")
    return redirect(url_for("dashboard"))

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your mail server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'venomcansec6@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'wayg lxmy jtrp qndi'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'venomcansec6@gmail.com'

mail = Mail(app)

# Fake database (replace this with your real user database)
users = {"canolowana5@.com": {"password": "hashed_password"}}

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        print(f"🔍 Checking email: {email}")  # Debugging

        try:
            user = auth.get_user_by_email(email)  # Fetch user from Firebase
            print(f"✅ User found: {user.email}")  # Debugging
            
            reset_tokens = secrets.token_urlsafe(20)
            reset_link = url_for('reset_password', token=reset_tokens, _external=True)

            msg = Message("Password Reset Request",
              recipients=[email],
              html=render_template_string("""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Password Reset Request</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            margin: 0;
                            padding: 20px;
                        }
                        .container {
                            max-width: 500px;
                            background: white;
                            padding: 20px;
                            margin: auto;
                            border-radius: 8px;
                            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                            text-align: center;
                        }
                        h2 {
                            color: #333;
                        }
                        p {
                            color: #555;
                            font-size: 16px;
                        }
                        .btn {
                            display: inline-block;
                            padding: 12px 20px;
                            color: white;
                            background-color: #007bff;
                            text-decoration: none;
                            border-radius: 5px;
                            font-size: 16px;
                            font-weight: bold;
                            margin-top: 20px;
                        }
                        .footer {
                            margin-top: 20px;
                            font-size: 14px;
                            color: #777;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Password Reset Request</h2>
                        <p>Hello,</p>
                        <p>You recently requested to reset your password. Click the button below to reset it:</p>
                        <a href="{{ reset_link }}" class="btn">Reset Password</a>
                        <p>If you did not request this, please ignore this email.</p>
                        <p class="footer">This link will expire in 24 hours.</p>
                    </div>
                </body>
                </html>
              """, reset_link=reset_link))


            print(f"📩 Sending email to: {email}")
            mail.send(msg)
            print("✅ Reset email sent!")

            flash("Reset password instructions have been sent to your email!", "success")
        except firebase_admin.auth.UserNotFoundError:
            print("⚠ Email not found in Firebase!")
            flash("Email not found!", "error")
        except Exception as e:
            print(f"❌ Firebase error: {e}")
            flash("Error fetching user from database", "error")

    return render_template('forgot-password.html')




@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if token not in reset_tokens:
        return "Invalid or expired token!", 400

    if request.method == 'POST':
        new_password = request.form['password']
        email = reset_tokens[token]  # Get email from stored tokens

        try:
            # Get user by email and update password
            user = auth.get_user_by_email(email)
            auth.update_user(user.uid, password=new_password)

            # Remove token after successful reset
            del reset_tokens[token]

            flash("Password reset successful! You can now log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error resetting password: {e}", "error")

    return render_template('reset-password.html')

if __name__ == "__main__":
    app.run(debug=True)
