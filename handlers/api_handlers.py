"""The handler file of all the REST Api's"""
from fastapi import Request
from fastapi.templating import Jinja2Templates

from processors.crawler import CrawlBlog
from processors.data_processor import get_key_from_redis


templates = Jinja2Templates(directory="templates")


async def get_blogs(request: Request, tag: str = ""):
    """Handler which renders the home page where all blogs will be shown.

    Returns:
        HTMLResponse: The HTML of home page.
    """
    return templates.TemplateResponse("/blog_home.html", {"request": request, "tag_name": tag})


async def get_blog_by_id(request: Request, post_id: str):
    """Handler which renders the blog page that is selected on the home.

    Returns:
        HTMLResponse: The HTML of home page.
    """
    post_url = await get_key_from_redis(post_id)
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
