import json

from fastapi import WebSocket

from processors.crawler import CrawlMedium


async def crawler_websocket(websocket: WebSocket):
    """The function that starts the websocket for listening and sending events."""
    await websocket.accept()
    while True:
        tag_data = await websocket.receive_json()
        crawl_obj = CrawlMedium(start_index=tag_data["page"], tag=tag_data["tag"])
        blogs = await crawl_obj.get_blogs()
        await websocket.send_text(json.dumps(blogs))
