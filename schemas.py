# schemas.py
from pydantic import BaseModel, EmailStr, Field, HttpUrl

# This class defines the structure of our form data and validates it
class ContactForm(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    website_url: HttpUrl | None = None
    message: str = Field(..., min_length=10, max_length=2000)
    recaptcha_token: str