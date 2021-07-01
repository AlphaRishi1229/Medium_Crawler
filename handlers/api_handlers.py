from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from constants import POST_ID_URL_CACHE
from processors.crawler import CrawlBlog


templates = Jinja2Templates(directory="templates")


async def get_blogs(request: Request):
    """Handler which renders the home page where all blogs will be shown.

    Returns:
        HTMLResponse: The HTML of home page.
    """
    return templates.TemplateResponse("/blog_home.html", {"request": request})


async def get_blog_by_id(request: Request, post_id: str):
    """Handler which renders the home page where all blogs will be shown.

    Returns:
        HTMLResponse: The HTML of home page.
    """
    post_url = POST_ID_URL_CACHE.get(post_id, None)
    crawler_obj = CrawlBlog(post_id)
    blog_data = await crawler_obj.get_blog_html(post_url)
    return templates.TemplateResponse(
        "/blog_data.html",
        {
            "request": request,
            "blog": blog_data["blogs"],
            "title": blog_data["title"],
            "tags": blog_data["tags"]
        }
    )
