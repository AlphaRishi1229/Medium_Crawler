from constants import GRAPHQL_PAYLOAD, MEDIUM_GRAPHQL_URL
from helpers.api_helpers import aiohttp_request


class CrawlMedium:
    def __init__(self, tag):
        self.start_index = 0
        self.limit = 10
        self.tag = tag

    async def get_blogs(self):
        parsed_blogs = []
        GRAPHQL_PAYLOAD["variables"]["tagSlug"] = self.tag
        response = await aiohttp_request(
            request_type="POST", url=MEDIUM_GRAPHQL_URL,
            data=GRAPHQL_PAYLOAD
        )
        blogs = response["json"].get("data", {}).get("tagFeed", {})
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
        return parsed_blogs

