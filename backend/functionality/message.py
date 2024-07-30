import os

from datetime import datetime

from mailersend import emails
from pydantic import BaseModel

from logger import log_green

USE_EMAIL = os.environ.get("EMAILS_ENABLED", "False")
API_KEY = os.environ.get("MAILERSENDER_API_KEY", "NO_KEY")
EMAIL_FROM = os.environ.get("EMAIL_ADDRESS", "NO_EMAIL")

class VoucherClaimEmailRequest(BaseModel):
    eatery_name: str
    voucher_name: str
    voucher_description: str
    voucher_expiry: datetime

class VoucherBookingEmailRequest(BaseModel):
    eatery_name: str
    voucher_name: str
    voucher_description: str
    voucher_code: str
    voucher_expiry: datetime

def send_customer_welcome_email(to_email: str, to_name: str):
    """
    Send a welcome email to a customer
    """
    subject = "Welcome to ChowDown!"
    html_text = f"""
                <h1>Welcome to ChowDown!</h1>
                <p>Hi {to_name}, and welcome to ChowDown!</p>
                <p>We're excited to have you on board as a customer. You can now start exploring eateries and making voucher bookings.</p>"""
    text = f"""Hi {to_name},\n\nWelcome to ChowDown! We're excited to have you on board as a customer. 
                You can now start exploring eateries and making voucher bookings.\n\nHappy dining!"""
    send_email(subject, to_email, to_name, text, html_text)

def send_eatery_welcome_email(to_email: str, to_name: str):
    """
    Send a welcome email to an eatery
    """
    subject = "Welcome to ChowDown!"
    html_text = f"""<h1>Welcome to ChowDown!</h1>
                    <p>Hi {to_name}, and welcome to ChowDown!</p>
                    <p>We're excited to have you on board as an eatery. You can now start creating voucher templates and managing your bookings.</p>"""
    text = f"""Hi {to_name},\n\nWelcome to ChowDown! We're excited to have you on board as an eatery. 
                You can now start creating voucher templates and managing your bookings.\n\nHappy dining!"""
    send_email(subject, to_email, to_name, text, html_text)

def send_voucher_claiming_email(to_email: str, to_name: str, voucher_request: VoucherClaimEmailRequest):
    """
    Send an email to a customer who has claimed a voucher
    """
    subject = "Voucher Claim Confirmation"
    html_text = f"""<h1>Voucher Claim Confirmation</h1>
                <p>Hi {to_name},</p>
                <p>Thank you for claiming a voucher with ChowDown! You have successfully claimed a voucher for {voucher_request.voucher_name}.</p>
                <p>Voucher Description: {voucher_request.voucher_description}</p>
                <p>This voucher expires {voucher_request.voucher_expiry}</p>"""
    text = f"""Hi {to_name},\n\nThank you for claiming a voucher with ChowDown! You have successfully claimed a voucher for {voucher_request.voucher_name}.\n\n
                Voucher Description: {voucher_request.voucher_description}\n\nThis voucher expires {voucher_request.voucher_expiry}"""
    send_email(subject, to_email, to_name, text, html_text)

def send_voucher_booking_email(to_email: str, to_name: str, voucher_request: VoucherBookingEmailRequest):
    """
    Send an email to a customer who has booked a voucher
    """
    subject = "Voucher Booking Confirmation"
    html_text = f"""<h1>Voucher Booking Confirmation</h1><p>Hi {to_name},</p>
                <p>Thank you for booking a voucher with ChowDown! Your booking at {voucher_request.eatery_name} has been confirmed and you are entitled to a voucher for {voucher_request.voucher_name}.</p>
                <p>Voucher Description: {voucher_request.voucher_description}</p>
                <p>This voucher expires {voucher_request.voucher_expiry}</p>
                <p>Please use the following code to redeem your voucher:</p>
                <p>Voucher Code: <strong>{voucher_request.voucher_code}</strong></p>
                """
    text=f"""Hi {to_name},\n\nThank you for booking a voucher with ChowDown! 
            Your booking at {voucher_request.eatery_name} has been confirmed and you are entitled to a voucher for {voucher_request.voucher_name}.\n\n
            Voucher Description: {voucher_request.voucher_description}\n\nThis voucher expires {voucher_request.voucher_expiry}\n\n
            Please use the following code to redeem your voucher:\n\nVoucher Code: {voucher_request.voucher_code}"""
    send_email(subject, to_email, to_name, text, html_text)

def send_email(subject: str, to_email: str, to_name: str, text: str, html_text: str = ""):
    """
    Send an email message
    """
    if USE_EMAIL == "True":
        _send_message(subject, to_email, to_name, text, html_text)

def _send_message(subject: str, to_email: str, to_name: str, text: str, html_text: str = ""):
    """
    Send an email message
    """
    mailer = emails.NewEmail(API_KEY)

    mail_body = {}

    mail_from = {
        "name": "ChowDown",
        "email": EMAIL_FROM,
    }

    receipients = [
        {
            "name": to_name,
            "email": to_email,
        }
    ]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(receipients, mail_body)
    mailer.set_subject(subject, mail_body)
    mailer.set_html_content(html_text, mail_body)
    mailer.set_plaintext_content(text, mail_body)

    res = mailer.send(mail_body)

    log_green(f"Email sent to {to_email} with status code {res}")
