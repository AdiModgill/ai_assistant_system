"""
Email Tool
==========
Sends emails via Gmail SMTP.
Requires SENDER_EMAIL and SENDER_PASSWORD in .env file.
Use a Gmail App Password, not your real password.
"""

import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()


class EmailTool:
    def __init__(self):
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")

    def send_email(self, recipient, subject, body):
        print(f"\n[EmailTool] Sending to: {recipient}")
        print(f"[EmailTool] Subject: {subject}")

        # Check credentials
        if not self.sender_email or not self.sender_password:
            return {
                "success": False,
                "error": "Email credentials missing. Add SENDER_EMAIL and SENDER_PASSWORD to your .env file"
            }

        # Validate recipient
        recipient = str(recipient).strip()
        if not recipient or "@" not in recipient:
            return {
                "success": False,
                "error": f"Invalid email address: {recipient}"
            }

        try:
            msg = EmailMessage()
            msg["From"] = self.sender_email
            msg["To"] = recipient
            msg["Subject"] = str(subject).strip()
            msg.set_content(str(body).strip())

            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            print(f"[EmailTool] ✅ Email sent successfully!")
            return {
                "success": True,
                "message": f"Email sent to {recipient}"
            }

        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "error": "Gmail login failed. Make sure you're using a Gmail App Password, not your regular password"
            }

        except smtplib.SMTPException as e:
            return {
                "success": False,
                "error": f"SMTP error: {str(e)}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }