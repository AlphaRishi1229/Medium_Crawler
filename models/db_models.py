from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


def get_ist_now():
    """Returns Indian Standard Time datetime object.

    Returns:
        object -- Datetime object
    """
    return datetime.now()


class Blogs(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)  # noqa
    post_id = Column(String(64))
    title = Column(String(1024))
    blog_desc = Column(String(3000))
    blog_data = Column(String)
    blog_link = Column(String(512))
    author_id = Column(Integer, ForeignKey("author.id"), index=True)
    created_time = Column(DateTime, default=str(get_ist_now()), index=True)
    read_time = Column(Integer)
    tags = Column(ARRAY(Integer, ForeignKey("tags.id")))

    __table_args__ = (
        UniqueConstraint(post_id, title, blog_desc, blog_data, blog_link, author_id, read_time, tags, name='_blogs_uc'),
        Index("idx_primary_identifier", "post_id"),
        Index("ix_combined_created_id", "post_id", "created_time"),
        Index("ix_created_on", "created_time")
    )


class Author(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True, index=True)  # noqa
    author_id = Column(String(64))
    author_name = Column(String(128))
    created_time = Column(DateTime, default=str(get_ist_now()), index=True)
    blogs = relationship("Blogs", backref="blogs")

    __table_args__ = (
        UniqueConstraint(author_id, author_name, name='_author_uc'),
        Index("idx_author", "author_id"),
        Index("ix_author_created_on", "created_time")
    )


class Tags(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)  # noqa
    tag_name = Column(String(64), unique=True)

    __table_args__ = (
        Index("ix_tag_name", "tag_name"),
    )
