from fastapi import Request
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")


async def show_blogs(request: Request):
    """Handler which renders the home page where all blogs will be shown.

    Returns:
        HTMLResponse: The HTML of home page.
    """
    return templates.TemplateResponse("/blog_home.html", {"request": request})
