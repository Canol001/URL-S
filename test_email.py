from flask_mail import Mail, Message
from flask import Flask
import os

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your mail server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'venomcansec6@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'wayg lxmy jtrp qndi'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'venomcansec6@gmail.com'

mail = Mail(app)

with app.app_context():
    try:
        msg = Message("Test Email",
                      recipients=["canolowana5@gmail.com"],
                      body="This is a test email from Flask.")
        mail.send(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email failed: {e}")
