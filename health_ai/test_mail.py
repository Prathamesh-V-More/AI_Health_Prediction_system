import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()
username = os.getenv("MAIL_USERNAME", "")
password = os.getenv("MAIL_PASSWORD", "")

print(f"Username: {username}")
print(f"Password length: {len(password)} chars")

try:
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    print("LOGIN SUCCESS!")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "AI Health System - Test Email"
    msg["From"]    = username
    msg["To"]      = username
    msg.attach(MIMEText("<h2 style='color:#2c7be5;'>Test email works! OTP and PDF reports will now be delivered.</h2>", "html"))
    server.sendmail(username, username, msg.as_string())
    server.quit()
    print(f"SUCCESS: Test email sent to {username}")
except smtplib.SMTPAuthenticationError as e:
    print(f"AUTH ERROR: {e}")
    print("Fix: Make sure App Password is correct and 2-Step Verification is ON")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
