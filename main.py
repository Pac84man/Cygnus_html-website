# main.py

# 1. Import the necessary tools from the FastAPI library
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# 2. Create an instance of the FastAPI application
# This 'app' variable is the main point of interaction for your web server.
app = FastAPI()

# 3. "Mount" the static files directory
# This tells FastAPI that any request that starts with "/static"
# should be served directly from the "static" folder in your project.
# This is how your CSS, JavaScript, and images will be loaded.
app.mount("/static", StaticFiles(directory="static"), name="static")

# 4. Set up the Jinja2 templating system
# This tells FastAPI where to find your HTML files.
# It points to the "templates" directory you created.
templates = Jinja2Templates(directory="templates")


# 5. Create a "route" for the homepage
# The decorator "@app.get('/')" tells FastAPI that the function below
# should handle any web browser requests for the main page of your website.
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    # Determine which template to use
    critical_template_path = "templates/index.critical.html"
    template_name = "index.critical.html" if os.path.exists(critical_template_path) else "index.html"

    # Render the chosen template
    return templates.TemplateResponse(template_name, {
        "request": request,
        "page_title": "Your Website, Reimagined"
    })

# --- Example for the future ---
# If you wanted to add a separate "Portfolio" page later, you would:
# 1. Create a portfolio.html file in your templates folder.
# 2. Add a new route here like this:
#
# @app.get("/portfolio", response_class=HTMLResponse)
# async def portfolio_page(request: Request):
#     return templates.TemplateResponse("portfolio.html", {
#         "request": request,
#         "page_title": "Our Work"
#     })
#