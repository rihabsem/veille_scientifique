import smtplib
import os
import resend

def send_email(email):
    sender = "no-reply@researchservice.com"
    recipient = email
    resend.api_key = os.getenv("EMAIL_RESEND_API")
    r = resend.Emails.send({
    "from": "no-reply@researchservice.dev",
    "to": email,
    "subject": "Notification de mise à jour de votre compte",
    "html": "Bonjour,\n\nNous vous informons que votre compte a été mis à jour avec succès.\n\nCordialement,\nL'équipe de recherche"
    })
    



