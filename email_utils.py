# email_utils.py
import os
import html
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from schemas import ContactForm

# We will no longer read the variables here.

async def send_contact_email(form_data: ContactForm):
    # --- THIS IS THE KEY CHANGE ---
    # We now read the environment variables from INSIDE the function.
    # This guarantees that load_dotenv() has already run.
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    EMAIL_FROM_ADDRESS = os.getenv('EMAIL_FROM_ADDRESS')
    EMAIL_TO_ADDRESS = os.getenv('EMAIL_TO_ADDRESS')

    if not all([SENDGRID_API_KEY, EMAIL_FROM_ADDRESS, EMAIL_TO_ADDRESS]):
        print("Email environment variables not set. Skipping email.")
        return

    # We use html.escape to sanitize user input for security
    name = html.escape(form_data.name)
    email = html.escape(form_data.email)
    website = html.escape(str(form_data.website_url)) if form_data.website_url else "Not provided"
    message_body = html.escape(form_data.message).replace('\n', '<br>')

    html_content = f"""
    <h3>New Contact Form Submission from Cygnus Website</h3>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Website:</strong> {website}</p>
    <hr>
    <p><strong>Message:</strong></p>
    <p>{message_body}</p>
    """

    message = Mail(
        from_email=EMAIL_FROM_ADDRESS,
        to_emails=EMAIL_TO_ADDRESS,
        subject="🚀 New Message from your Cygnus Website!",
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent with status code: {response.status_code}")
    except Exception as e:
        # We print errors but don't crash the app if email fails
        print(f"Error sending email: {e}")