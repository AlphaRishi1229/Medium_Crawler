import json

from fastapi import WebSocket

from processors.crawler import CrawlMedium


async def crawler_websocket(websocket: WebSocket):
    await websocket.accept()
    while True:
        tag = await websocket.receive_text()
        crawl_obj = CrawlMedium(tag=tag)
        blogs = await crawl_obj.get_blogs()
        await websocket.send_text(json.dumps(blogs))
