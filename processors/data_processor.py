"""The helper file for all the data related operations."""
from copy import deepcopy
from typing import Dict, List

from sqlalchemy.sql.sqltypes import Boolean

import aioredis

from constants import REDIS_CACHE_EXPIRY
from helpers.database_helpers import get_db_session
from helpers.redis_helper import RedisSession
from models.db_models import Author, Blogs, Tags


def get_blog_from_db(blog_id: str) -> Dict:
    """Returns the blog data from db.

    Args:
        blog_id (str): The blog id received from the frontend.

    Returns:
        Dict: The blog data.
        {
            "blog_id": blog_id,
            "title": db_blog.title,
            "blogs": db_blog.blog_data,
            "tags": [tag.tag_name for tag in db_tags]
        }
    """
    session = get_db_session()
    blog_data = {}
    try:
        db_blog: Blogs = session.query(Blogs).filter(
            Blogs.post_id == blog_id
        ).one()
        if db_blog:
            db_tags: List[Tags] = session.query(Tags).filter(
                Tags.id.in_(list(db_blog.tags))
            ).all()
            blog_data = {
                "blog_id": blog_id,
                "title": db_blog.title,
                "blogs": db_blog.blog_data,
                "tags": [tag.tag_name for tag in db_tags]
            }

    except Exception as e:
        print(e)

    return blog_data


def push_data_to_db(blogs: List) -> None:
    """The functions adds new data to the database.

    Args:
        blogs (List): The list of blogs in bulk to add in the database.
    """
    blog_data = deepcopy(blogs)
    session = get_db_session()

    author_objects = []
    blog_objects = []
    tag_objects = []

    author_ids = set()
    blog_ids = set()
    tag_names = set()

    author_map = {}

    try:
        authors: List[Author] = session.query(Author).filter(
            Author.author_id.in_([data["author_id"] for data in blog_data])
        ).all()
        db_blogs: List[Blogs] = session.query(Blogs).filter(
            Blogs.post_id.in_([data["post_id"] for data in blog_data])
        ).all()
        db_tags: List[Tags] = session.query(Tags).filter(
            Tags.tag_name.in_([data["tags"] for data in blog_data])
        ).all()

        # Add data to author and tags table.
        author_ids = set(author.author_id for author in authors)
        tag_names = set(tag.tag_name for tag in db_tags)

        for data in blog_data:
            data.pop("post_created_time")
            author_name = data.pop("creator")
            if data.get("author_id") not in author_ids:
                author_ids.add(data.get("author_id"))
                author_data = {
                    "author_id": data.get("author_id"),
                    "author_name": author_name
                }
                author_objects.append(Author(**author_data))
            if data.get("tags") not in tag_names:
                tag_names.add(data.get("tags"))
                tag_data = {
                    "tag_name": data.get("tags")
                }
                tag_objects.append(Tags(**tag_data))

        if author_objects:
            session.bulk_save_objects(author_objects)
            session.commit()
            authors: List[Author] = session.query(Author).filter(
                Author.author_id.in_(list(author_ids))
            ).all()

        if tag_objects:
            session.bulk_save_objects(tag_objects)
            session.commit()
            db_tags: List[Tags] = session.query(Tags).filter(
                Tags.tag_name.in_(list(tag_names))
            ).all()

        author_map = {author.author_id: author.id for author in authors}
        tag_map = {tag.tag_name: tag.id for tag in db_tags}

        # Add data to blogs table.
        blog_ids = set(blog.post_id for blog in db_blogs)

        for data in blog_data:
            if data["post_id"] not in blog_ids:
                data["author_id"] = author_map[data["author_id"]]
                data["tags"] = [tag_map[data["tags"]]]
                blog_objects.append(Blogs(**data))

        if blog_objects:
            session.bulk_save_objects(blog_objects)
            session.commit()

    except Exception as e:
        print(e)
        session.rollback()


def update_data_in_db(blog_data: Dict) -> None:
    """Updates the blog data in the database. Updates data like the html rendered data.

    Args:
        blog_data (Dict): The data to be updated mainly tags and html data.
    """
    session = get_db_session()

    all_tags = blog_data["tags"]
    new_tags = []

    try:
        db_tags: List[Tags] = session.query(Tags).filter(
            Tags.tag_name.in_(all_tags)
        ).all()
        present_tags = set(tag.tag_name for tag in db_tags)

        for tag in blog_data["tags"]:
            if tag not in present_tags:
                present_tags.add(tag)
                tag_data = {
                    "tag_name": tag
                }
                new_tags.append(Tags(**tag_data))

        if new_tags:
            session.bulk_save_objects(new_tags)
            session.commit()
            db_tags: List[Tags] = session.query(Tags).filter(
                Tags.tag_name.in_(list(present_tags))
            ).all()

        tag_map = {tag.tag_name: tag.id for tag in db_tags}

        db_blog: List[Blogs] = session.query(Blogs).filter(
            Blogs.post_id == blog_data["blog_id"]
        )
        update_data = {
            "tags": [tag_map[tag] for tag in all_tags],
            "blog_data": str(blog_data["blogs"])
        }

        db_blog.update(update_data, synchronize_session="evaluate")
        session.commit()

    except Exception as e:
        print(e)
        session.rollback()


async def bulk_update_to_redis(update_data: Dict) -> Boolean:
    """Adds keys and values to redis in bulk. Key here will be the blog id and value will be the url.

    Args:
        update_data (Dict): The key value pairs dictionary

    Returns:
        Boolean: True on completion.
    """
    redis_obj: aioredis.Redis = await RedisSession().get_redis_obj()
    redis_pipeline = redis_obj.pipeline()
    for key, value in update_data.items():
        redis_pipeline.setex(key, REDIS_CACHE_EXPIRY, value)
    try:
        await redis_pipeline.execute()
    except Exception as e:
        print(e)
    redis_obj.close()
    return True


async def get_key_from_redis(key: str) -> str:
    """Returns the value of a particular key from redis.

    Args:
        key (str): The key stored in redis.

    Returns:
        str: The value of the sent key.
    """
    redis_obj: aioredis.Redis = await RedisSession().get_redis_obj()
    value = await redis_obj.get(key, encoding="utf-8")
    redis_obj.close()
    return value
