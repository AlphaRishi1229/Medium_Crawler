from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


master_engine = None


def get_master_engine():
    """get_master_engine."""
    global master_engine

    if not master_engine:
        master_engine = create_engine(
            "postgresql+psycopg2://gocomet_read_write:goCometCrawler123@postgresql/gocomet_crawler",
            pool_recycle=3600,
            pool_size=10,
            pool_timeout=1,
            echo=False,
            max_overflow=5,
            convert_unicode=True,
            client_encoding="utf8",
        )
    return master_engine


def get_db_session():
    sesion_factory = scoped_session(sessionmaker(bind=get_master_engine()))
    return sesion_factory()
