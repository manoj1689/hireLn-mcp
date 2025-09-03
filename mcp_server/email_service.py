import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import traceback

# Load environment variables from .env
load_dotenv()

class EmailService:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        
        self.username = os.getenv("EMAIL_ADDRESS")
        self.password = os.getenv("EMAIL_PASSWORD")

    def send_email(self, to, subject, body, html_body=None):
        try:
            msg = MIMEText(body, "plain")
            msg["Subject"] = subject
            msg["From"] = self.username
            msg["To"] = to

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.set_debuglevel(1)   # 👈 shows SMTP conversation
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, [to], msg.as_string())

            print(f"✅ Email sent successfully to {to}")
            return True

        except Exception as e:
            print("❌ Failed to send email:", e)
            traceback.print_exc()  # shows full Gmail rejection
            return False
