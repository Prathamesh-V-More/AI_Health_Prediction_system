import sys, os
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv(override=True)

from app import create_app, mail
from flask_mail import Message

app = create_app()
with app.app_context():
    print("MAIL_USERNAME:", app.config.get("MAIL_USERNAME"))
    print("MAIL_PASSWORD length:", len(app.config.get("MAIL_PASSWORD", "")))
    print("MAIL_SUPPRESS_SEND:", app.config.get("MAIL_SUPPRESS_SEND"))
    try:
        msg = Message(
            subject="AI Health - OTP Test",
            recipients=[app.config.get("MAIL_USERNAME")],
            html="<h2>Your OTP is: <b style='color:#2c7be5;'>123456</b></h2>"
        )
        mail.send(msg)
        print("EMAIL SENT SUCCESSFULLY!")
    except Exception as e:
        print(f"SEND ERROR: {type(e).__name__}: {e}")
