from flask import Flask, request, render_template, jsonify
from werkzeug.utils import redirect
from dotenv import load_dotenv
import os
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest, CONTENT_TYPE_LATEST
import random
import time
app = Flask(__name__)

load_dotenv()

FORM_SUBMIT_COUNT = Counter('form_submit_total', 'Total form submits')
EMAIL_RECEIVED_COUNT = Counter('emails_received_total', 'Total emails received')
EMAIL_ACKNOWLEDGMENT_COUNT = Counter('emails_acknowledgment_total', 'Total acknowledgment emails sent')
EMAIL_ERROR_COUNT = Counter('emails_error_total', 'Total email errors')

# COUNTER: Total HTTP requests
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')

# GAUGE: Randomly fluctuating value (simulate memory, queue, or online users)
ACTIVE_USERS = Gauge('active_users', 'Number of active users')

# HISTOGRAM: Duration buckets (for tracking request time)
REQUEST_LATENCY_HIST = Histogram('request_latency_seconds', 'Request latency in seconds')

# SUMMARY: Like histogram, but with quantiles
REQUEST_LATENCY_SUMMARY = Summary('request_latency_summary_seconds', 'Request latency summary in seconds')

@app.route('/')
def home():
    # Gauge example: Set active users (simulate a change)
    ACTIVE_USERS.set(random.randint(1, 10))  # this would normally come from app logic

    # Histogram + Summary timing
    start = time.time()
    with REQUEST_LATENCY_HIST.time():  # Histogram timing
        time.sleep(random.uniform(0.1, 0.5))  # Simulate response latency

    duration = time.time() - start
    REQUEST_LATENCY_SUMMARY.observe(duration)  # Summary timing

    return render_template('index.html')  # This will render your HTML form

@app.route('/contact', methods=['POST'])
def search():
    FORM_SUBMIT_COUNT.inc()  # Count form submits
    name = request.form['full_name']
    sender_email = os.getenv("MAIL_ID") # Mail id is defined in the .env file create one and give your own
    receiver_email = request.form['email_address']
    password = os.getenv("APP_PASS")  #app password is defined in the .env file create one and give your own

    if not receiver_email or not name:
        return jsonify({'message': "Please enter Email and Name"})

    body = request.form['body']
    self_subject = f"Contact mail from {name}, {request.form['subject']}"
    self_mail = send_mail(sender_email, sender_email, self_subject, body, password)
    if self_mail:
        EMAIL_RECEIVED_COUNT.inc()  # Count email to self
    else:
        EMAIL_ERROR_COUNT.inc()

    ack_subject = "Thank you for contacting Pronoy"
    ack_body = f"I will reach out to you in 24 hrs through mail. Thank you for contacting."
    acknowledgement = send_mail(sender_email, receiver_email, ack_subject, ack_body, password)
    if acknowledgement:
        EMAIL_ACKNOWLEDGMENT_COUNT.inc()  # Count acknowledgement email
        return jsonify({'message': f"Thank You {name}, Will reach out to you soon!"})
    else:
        EMAIL_ERROR_COUNT.inc()  # Count email errors
        return jsonify({'message': f"Some Error!"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

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
    app.run(host="0.0.0.0", port=5000, debug=True)
