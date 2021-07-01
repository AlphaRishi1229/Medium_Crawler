from datetime import datetime
from math import ceil

from bs4 import BeautifulSoup

from constants import GRAPHQL_PAYLOAD, MEDIUM_GRAPHQL_URL
from constants import POST_ID_URL_CACHE
from helpers.api_helpers import aiohttp_request
from processors.data_processor import push_data_to_db


class CrawlMedium:
    def __init__(self, start_index, tag):
        self.start_index = start_index
        self.limit = 10
        self.tag = tag

    async def get_blogs(self):
        parsed_blogs = []
        GRAPHQL_PAYLOAD["variables"]["tagSlug"] = self.tag
        GRAPHQL_PAYLOAD["variables"]["paging"]["to"] = str(self.start_index)
        current_datetime = int(datetime.timestamp(datetime.now()))
        response = await aiohttp_request(
            request_type="POST", url=MEDIUM_GRAPHQL_URL,
            data=GRAPHQL_PAYLOAD
        )
        blogs = response["json"].get("data", {}).get("tagFeed", {})
        if blogs:
            for blog in blogs.get("items", []):
                post_date = datetime.fromtimestamp(blog["post"]["firstPublishedAt"] // 1000)
                post_created_on = (current_datetime - (blog["post"]["firstPublishedAt"] // 1000)) // (60 * 60)
                parsed_blogs.append(
                    {
                        # Blog DB Data
                        "post_id": blog["post"]["id"],
                        "title": blog["post"]["title"],
                        "blog_desc": blog["post"]["previewContent"]["subtitle"],
                        "blog_data": "",
                        "blog_link": blog["post"]["mediumUrl"],
                        "created_time": post_date.isoformat(),
                        "read_time": ceil(blog["post"]["readingTime"]),
                        "tags": [self.tag],
                        # Author DB Data
                        "author_id": blog["post"]["creator"]["id"],
                        "creator": blog["post"]["creator"]["name"],
                        # Extra Meta
                        "post_created_time": post_created_on,
                    }
                )
                POST_ID_URL_CACHE[blog["post"]["id"]] = blog["post"]["mediumUrl"]
            push_data_to_db(parsed_blogs)

        return parsed_blogs


class CrawlBlog:
    def __init__(self, blog_id: str = ""):
        self.blog_id = blog_id

    async def get_blog_html(self, url):
        response = await aiohttp_request(request_type="GET", url=url)
        soup_obj = BeautifulSoup(response["content"], "html.parser")
        all_data = soup_obj.find("div", class_="s")
        blogs_data = all_data.find("article")
        blog_title = blogs_data.find("h1")
        tags_data = all_data.find_all("ul")[-1].find_all("a")
        post_tags = [tag.text for tag in tags_data]
        final_data = {
            "title": blog_title,
            "blogs": blogs_data,
            "tags": tags_data,
        }
        return final_data
