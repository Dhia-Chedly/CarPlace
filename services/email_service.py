import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT", 587)
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

def send_otp_email(email_to: str, otp_code: str):
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS]):
        print("Warning: SMTP settings not fully configured. Email not sent.")
        print(f"OTP for {email_to} is: {otp_code}")
        return

    msg = MIMEMultipart()
    msg['From'] = SMTP_FROM
    msg['To'] = email_to
    msg['Subject'] = "Your CarPlace 2FA Code"

    body = f"Your one-time password (OTP) for login is: {otp_code}. It expires in 5 minutes."
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_HOST, int(SMTP_PORT))
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        print(f"OTP sent successfully to {email_to}")
    except Exception as e:
        print(f"Error sending email: {e}")
