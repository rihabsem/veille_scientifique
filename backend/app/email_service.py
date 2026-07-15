import smtplib
import os
import resend

def send_email(email):
    print(f"Sending email to {email}")
    resend.api_key = os.getenv("EMAIL_RESEND_API")
    r = resend.Emails.send({
    "from": "onboarding@resend.dev",
    "to": email,
    "subject": "Notification de mise à jour de votre compte",
    "html": """
    <p>Bonjour,</p>

    <p>Nous vous informons que votre compte a été mis à jour avec succès.</p>

    <p>Ne répondez pas à cet e-mail, il s'agit d'une notification automatique.</p>

    <p>Cordialement,<br>
    L'équipe de recherche</p>
    """
    })

    



