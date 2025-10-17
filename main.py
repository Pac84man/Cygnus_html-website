# main.py
import os
import asyncpg # <-- We use this directly now
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from dotenv import load_dotenv
import httpx

# --- IMPORTS FOR OUR NEW STRUCTURE ---
from email_utils import send_contact_email
from schemas import ContactForm

load_dotenv()

# --- Configuration & Setup ---
DATABASE_URL = os.getenv("DATABASE_URL")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])
app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --- The Secure API Endpoint (with direct asyncpg connection) ---
@app.post("/api/contact")
@limiter.limit("5/minute")
async def handle_contact_form(request: Request, form_data: ContactForm):
    # 1. Verify reCAPTCHA token (no change here)
    async with httpx.AsyncClient() as client:
        response = await client.post("https://www.google.com/recaptcha/api/siteverify", data={
            "secret": RECAPTCHA_SECRET_KEY, "response": form_data.recaptcha_token, "remoteip": request.client.host
        })
        result = response.json()

    if not result.get("success") or result.get("score", 0.0) < 0.5:
        raise HTTPException(status_code=400, detail="reCAPTCHA verification failed. Are you a robot?")

    # 2. Connect to the database, execute, and disconnect within the request
    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        query = "INSERT INTO contacts (name, email, website_url, message) VALUES ($1, $2, $3, $4)"
        await conn.execute(query,
            form_data.name,
            form_data.email,
            str(form_data.website_url) if form_data.website_url else None,
            form_data.message
        )
        # 3. Send email AFTER database success
        await send_contact_email(form_data)
    except Exception as e:
        print(f"Database or Email error: {e}")
        raise HTTPException(status_code=500, detail="Could not save your message. Please try again later.")
    finally:
        # 4. Guarantee the connection is closed
        if conn:
            await conn.close()

    return {"message": "Thank you! Your message has been sent successfully."}


# --- The Main Page Route (no change here) ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    template_name = "index.critical.html"
    if not os.path.exists(os.path.join("templates", template_name)):
        template_name = "index.html"
    return templates.TemplateResponse(template_name, {"request": request})