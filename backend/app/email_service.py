import smtplib
import os
# import resend
from email.message import EmailMessage
from mistralai.client import Mistral

EMAIL_ADDRESS = "researchserviceerasme@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSKEY")

def generate_email(articles):
    if not articles:
        return None
    
    combined_text = " ".join([a.get("abstract", "") for a in articles if a.get("abstract")])
    if not combined_text.strip():
        return None
    
    query = f"""
    ROLE:
    You are a medical research assistant specialized in summarizing scientific literature.

    TASK:
    Generate a concise synthesis of the scientific updates based on the abstracts of the articles provided.

    CONTEXT:
    {articles}

    INSTRUCTIONS:
    - Analyze all the abstracts collectively rather than individually.
    - Produce a single, coherent paragraph in French.
    - Highlight only the main scientific trends, emerging findings, or notable advances shared across the articles.
    - Synthesize the information instead of listing or describing each article separately.
    - Do not mention article titles, authors, or journals.
    - Do not define medical concepts or provide background explanations.
    - Focus only on the key insights that the reader should take away from these recent publications.
    - Keep the summary concise (approximately 80–150 words).
    - Avoid repetition and speculative statements.

    IMPORTANT:
    - The output MUST be written entirely in French.
    - Return only the summary, with no headings, bullet points, or introductory text.
    """
    client = Mistral(api_key=os.getenv("MISTRAL_KEY"))
    response = client.chat.complete(
        model="mistral-small-2603",
        messages=[
            {"role":"user", "content":query}
        ],
    )
    return response.choices[0].message.content

def send_email(to_email, articles):
    msg = EmailMessage()
    msg["Subject"] = "Notification de mise à jour de votre compte"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    objet = generate_email(articles)
    if objet is None:
        return
    print(objet)
    msg.set_content(f"""
    Des nouvelles mise a jour sont disponible sur votre compte:
    Voici un resumé récapitulatif:
    {objet}
    """)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print(f"Email sent successfully to {to_email}")

    except Exception as e:
        print(f"Failed to send email: {e}")


# if __name__ == "__main__":
#     send_email(
#         to_email="rihabalx@gmail.com"
#     )



    



