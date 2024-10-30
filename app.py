from flask import Flask, request, render_template, jsonify
from werkzeug.utils import redirect
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

@app.route('/')
def home():
    return render_template('index.html')  # This will render your HTML form

@app.route('/contact', methods=['POST'])
def search():
    name = request.form['full_name']
    sender_email = os.getenv("MAIL_ID") # Mail id is defined in the .env file create one and give your own
    receiver_email = request.form['email_address']
    password = os.getenv("APP_PASS")  #app password is defined in the .env file create one and give your own

    if not receiver_email or not name:
        return jsonify({'message': "Please enter Email and Name"})

    body = request.form['body']
    self_subject = f"Contact mail from {name}, {request.form['subject']}"
    self_mail = send_mail(sender_email, sender_email, self_subject, body, password)

    ack_subject = "Thank you for contacting Pronoy"
    ack_body = f"I will reach out to you in 24 hrs through mail. Thank you for contacting."
    acknowledgement = send_mail(sender_email, receiver_email, ack_subject, ack_body, password)
    if acknowledgement:
        return jsonify({'message': f"Thank You {name}, Will reach out to you soon!"})
    else:
        return jsonify({'message': f"Some Error!"})

def send_mail(sender_email, receiver_email, subject, body, password):
    import smtplib
    from email.mime.text import MIMEText

    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())  # Send the email
    return 1

if __name__ == '__main__':
    app.run(debug=True)
