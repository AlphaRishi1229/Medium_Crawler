from datetime import datetime
from math import ceil
from typing import Dict, List

from bs4 import BeautifulSoup

from constants import GRAPHQL_PAYLOAD, MEDIUM_GRAPHQL_URL
from helpers.api_helpers import aiohttp_request
from processors.data_processor import get_blog_from_db, push_data_to_db, update_data_in_db
from processors.data_processor import bulk_update_to_redis


class CrawlMedium:
    """The class that crawls the medium.com website to get all blogs."""
    def __init__(self, start_index: int, tag: str):
        """The constructor of the class.

        Args:
            start_index (int): Pagination
            tag (str): The tag to be searched.
        """
        self.start_index = start_index
        self.limit = 10
        self.tag = tag.lower()

    async def get_blogs(self) -> List:
        """The main function that crawls 10 pages on medium.com for the given tag.

        Also stores the data in database and updates blog id and url in redis for quick access,

        Returns:
            List: The list of crawled blogs.
        """
        parsed_blogs = []
        GRAPHQL_PAYLOAD["variables"]["tagSlug"] = self.tag
        GRAPHQL_PAYLOAD["variables"]["paging"]["to"] = str(self.start_index)
        current_datetime = int(datetime.timestamp(datetime.now()))
        post_id_url_map = {}
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
                        "tags": self.tag,
                        # Author DB Data
                        "author_id": blog["post"]["creator"]["id"],
                        "creator": blog["post"]["creator"]["name"],
                        # Extra Meta
                        "post_created_time": post_created_on,
                    }
                )
                post_id_url_map[blog["post"]["id"]] = blog["post"]["mediumUrl"]

            await bulk_update_to_redis(post_id_url_map)
            push_data_to_db(parsed_blogs)

        return parsed_blogs


class CrawlBlog:
    """This class crawls a partitular blog using BeautifulSoup."""
    def __init__(self, blog_id: str = ""):
        """Constructor for the class.

        Args:
            blog_id (str, optional): The blog id to be crawled. Defaults to "".
        """
        self.blog_id = blog_id

    async def get_blog_html(self, url: str) -> Dict:
        """The main function which crawls the blog.

        Checks in the database first if it has been crawled before and if not then crawls it.
        Args:
            url (str): The url of the blog to be crawled.

        Returns:
            Dict: The data that has been crawled from the given url.
        """
        final_data = get_blog_from_db(self.blog_id)
        if not final_data["blogs"]:
            response = await aiohttp_request(request_type="GET", url=url)
            soup_obj = BeautifulSoup(response["content"], "html.parser")
            all_data = soup_obj.find("div", class_="s")
            blogs_data = all_data.find("article")
            blog_title = blogs_data.find("h1")
            tags_data = all_data.find_all("ul")[-1].find_all("a")
            post_tags = [tag.text for tag in tags_data]
            final_data = {
                "blog_id": self.blog_id,
                "title": blog_title,
                "blogs": blogs_data,
                "tags": post_tags,
            }
            update_data_in_db(final_data)

        return final_data
