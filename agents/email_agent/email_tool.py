import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()


class EmailTool:
    """
    A tool that sends emails via Gmail SMTP.
    Uses EmailMessage instead of MIME classes.
    """
    
    def __init__(self):
        """Initialize with Gmail credentials from .env file"""
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
    
    def send_email(self, recipient, subject, body):
        """
        Send an email using Gmail SMTP.
        
        Args:
            recipient: Email address to send to
            subject: Email subject
            body: Email message content
        
        Returns:
            dict with success status
        """
        
        print(f"\n[EmailTool] send_email called")
        print(f"[EmailTool] recipient: {recipient}")
        print(f"[EmailTool] subject: {subject}")
        print(f"[EmailTool] body: {body}")
        
        # Validate credentials
        if not self.sender_email or not self.sender_password:
            return {
                "success": False,
                "error": "Email credentials missing in .env file"
            }
        
        # Make sure everything is a string
        recipient = str(recipient).strip()
        subject = str(subject).strip()
        body = str(body).strip()
        
        print(f"[EmailTool] After string conversion:")
        print(f"[EmailTool] recipient: {recipient} (type: {type(recipient)})")
        print(f"[EmailTool] subject: {subject} (type: {type(subject)})")
        print(f"[EmailTool] body: {body} (type: {type(body)})")
        
        # Validate recipient
        if not recipient or "@" not in recipient:
            return {
                "success": False,
                "error": f"Invalid email: {recipient}"
            }
        
        try:
            print(f"[EmailTool] Creating EmailMessage object")
            
            # Create message using EmailMessage (newer, simpler API)
            msg = EmailMessage()
            msg["From"] = self.sender_email
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.set_content(body)
            
            print(f"[EmailTool] Message created successfully")
            print(f"[EmailTool] Connecting to Gmail SMTP server")
            
            # Connect to Gmail SMTP server
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
            
            print(f"[EmailTool] Connected to SMTP server")
            print(f"[EmailTool] Logging in with email: {self.sender_email}")
            
            server.login(self.sender_email, self.sender_password)
            
            print(f"[EmailTool] Logged in successfully")
            print(f"[EmailTool] Sending email...")
            
            # Send the email
            server.send_message(msg)
            
            print(f"[EmailTool] Email sent successfully!")
            
            # Close connection
            server.quit()
            
            return {
                "success": True,
                "message": f"Email sent to {recipient}"
            }
        
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EmailTool] SMTP Authentication Error: {e}")
            return {
                "success": False,
                "error": f"Gmail authentication failed. Check your app password. Error: {str(e)}"
            }
        
        except smtplib.SMTPException as e:
            print(f"[EmailTool] SMTP Exception: {e}")
            return {
                "success": False,
                "error": f"SMTP Error: {str(e)}"
            }
        
        except Exception as e:
            print(f"[EmailTool] General Exception: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
        