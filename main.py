# main.py
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field, HttpUrl # This import remains
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from dotenv import load_dotenv
import httpx
from databases import Database

# --- IMPORTS FOR OUR NEW STRUCTURE ---
from email_utils import send_contact_email
from schemas import ContactForm  # <-- THIS IS THE NEW, CORRECT IMPORT

# Load all the secrets from our .env file
load_dotenv()

# --- Configuration & Setup ---
DATABASE_URL = os.getenv("DATABASE_URL")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

# Initialize the database connection
database = Database(DATABASE_URL)

# Initialize the rate limiter (e.g., 5 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])

# Initialize the FastAPI app and add the rate limiting middleware
app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Mount static files and setup Jinja2 templates (no change here)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- THE 'ContactForm' CLASS HAS BEEN MOVED TO 'schemas.py' ---
# It no longer lives here.

# --- Database Lifecycle Events ---
@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# --- The Secure API Endpoint ---
@app.post("/api/contact")
@limiter.limit("5/minute")
async def handle_contact_form(request: Request, form_data: ContactForm): # This line works because we imported ContactForm from schemas.py
    # 1. Verify reCAPTCHA token with Google's server
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": RECAPTCHA_SECRET_KEY,
                "response": form_data.recaptcha_token,
                "remoteip": request.client.host,
            },
        )
        result = response.json()

    if not result.get("success") or result.get("score", 0.0) < 0.5:
        raise HTTPException(status_code=400, detail="reCAPTCHA verification failed. Are you a robot?")

    # 2. Insert the validated data into our Supabase database
    try:
        query = "INSERT INTO contacts (name, email, website_url, message) VALUES (:name, :email, :website_url, :message)"
        await database.execute(query=query, values={
            "name": form_data.name,
            "email": form_data.email,
            "website_url": str(form_data.website_url) if form_data.website_url else None,
            "message": form_data.message
        })
    except Exception as e:
        print(f"Database insertion error: {e}")
        raise HTTPException(status_code=500, detail="Could not save your message. Please try again later.")

    # 3. If the database insert was successful, send the email notification
    await send_contact_email(form_data)

    return {"message": "Thank you! Your message has been sent successfully."}


# --- The Main Page Route (no change here) ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    template_name = "index.critical.html"
    if not os.path.exists(os.path.join("templates", template_name)):
        template_name = "index.html"
    return templates.TemplateResponse(template_name, {"request": request})