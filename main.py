import requests

from fastapi import FastAPI

from constants import GRAPHQL_PAYLOAD, MEDIUM_GRAPHQL_URL, MEDIUM_TAG_URL
from urls import blogs_api_router, websocket_v1_router


app = FastAPI(
    title="GoComet - Web Crawler",
    description="""This project scrapes/crawls through blogs on medium.com""",
    version="1.0.0",
    docs_url="/docs/swagger",
    redoc_url="/docs/redoc",
    openapi_url="/swagger.json",
)


@app.get("/", tags=["System Check"])
async def root():
    return {"status": True}


app.include_router(blogs_api_router)
app.include_router(websocket_v1_router)


@app.get("/api/crawler")
async def api_crawler():
    parsed_blogs = []
    GRAPHQL_PAYLOAD["variables"]["tagSlug"] = "python"
    req = requests.post(MEDIUM_GRAPHQL_URL, json=GRAPHQL_PAYLOAD)
    response_body = req.json()
    blogs = response_body["data"]["tagFeed"]
    if blogs:
        for blog in blogs.get("items", []):
            parsed_blogs.append(
                {
                    "creator": blog["post"]["creator"]["name"],
                    "title": blog["post"]["title"],
                    "blog": blog["post"]["previewContent"]["subtitle"],
                    "blog_link": blog["post"]["mediumUrl"],
                    "created_time": blog["post"]["firstPublishedAt"],
                    "read_time": blog["post"]["readingTime"],
                }
            )

    print(parsed_blogs)
    return {"message": "Hello World"}


@app.get("/soup/crawler")
async def web_crawler():
    parsed_blogs = []
    crawl_url = MEDIUM_TAG_URL.format("python")
    req = requests.get(crawl_url)
    soup = BeautifulSoup(req.content, 'html.parser')
    blogs = soup.find_all("div", class_="ae em")
    for blog in blogs:
        head = blog.find("div", class_="fj l")
        body = blog.find("div", class_="fv l").a
        creator = head.h4.text
        title = body.h2.text
        if body.h3:
            brief = body.h3.text
        else:
            brief = ""
        href = body.get("href")
        created_time = body.p.text
        read_time = body.find("span", class_="ay b dj ei dm").text

        parsed_blogs.append(
            {
                "creator": creator,
                "title": title,
                "blog": brief,
                "blog_link": href,
                "created_time": created_time,
                "read_time": read_time
            }
        )

    print(parsed_blogs)
    return {"message": "Hello World"}
