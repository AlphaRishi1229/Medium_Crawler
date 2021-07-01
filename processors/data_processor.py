from copy import deepcopy
from typing import List

from sqlalchemy import exc

from helpers.database_helpers import get_db_session
from models.db_models import Author, Blogs

def push_data_to_db(blogs: List):
    blog_data = deepcopy(blogs)
    session = get_db_session()

    author_objects = []
    blog_objects = []
    author_ids = set()
    blog_ids = set()

    author_map = {}

    try:
        authors: List[Author] = session.query(Author).filter(
            Author.author_id.in_([data["author_id"] for data in blog_data])
        ).all()
        db_blogs: List[Blogs] = session.query(Blogs).filter(
            Blogs.post_id.in_([data["post_id"] for data in blog_data])
        ).all()


        for author in authors:
            author_ids.add(author.author_id)

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

        if author_objects:
            session.bulk_save_objects(author_objects)
            session.commit()
            authors: List[Author] = session.query(Author).filter(
                Author.author_id.in_([data["author_id"] for data in blog_data])
            ).all()

        for author in authors:
            author_map[author.author_id] = author.id


        for blog in db_blogs:
            blog_ids.add(blog.post_id)

        for data in blog_data:
            if data["post_id"] not in blog_ids:
                data["author_id"] = author_map[data["author_id"]]
                blog_objects.append(Blogs(**data))

        if blog_objects:
            session.bulk_save_objects(blog_objects)
            session.commit()

    except exc.IntegrityError:
        session.rollback()
