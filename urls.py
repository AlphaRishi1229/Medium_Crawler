from fastapi import APIRouter
from starlette.routing import WebSocketRoute

from handlers.api_handlers import get_blog_by_id, get_blogs
from handlers.websocket_handlers import crawler_websocket


api_v1_router = APIRouter(
    prefix="/api/v1",
    tags=["v1 APIs"],
    responses={404: {"description": "Url Not found"}},
)

blogs_api_router = APIRouter(
    prefix="/blogs",
    tags=["Blogs Related APIs"],
    responses={404: {"description": "Url Not found"}},
)

websocket_v1_router = APIRouter(
    tags=["v1 WebSockets"],
    responses={
        404: {"description": "Websocket Not found"},
        403: {"description": "Websocket Connection Not Established"}
    },
)

# Api for blogs home page.
blogs_api_router.add_api_route("/", get_blogs, methods=["GET"])
blogs_api_router.add_api_route("/{post_id}", get_blog_by_id, methods=["GET"])

# Websocket for powering the admin panel for blogs.
websocket_v1_router.add_websocket_route("/ws/v1/blogs/crawler", crawler_websocket)
