""" Database functionality for Product Database Service """
from sqlmodel import create_engine, SQLModel, Session
from product_db import setting


connection_string: str = str(setting.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg")
engine = create_engine(connection_string, connect_args={},
                       pool_recycle=300, pool_size=10)


def create_tables() -> None:
    """ Function to create tables in database """
    SQLModel.metadata.create_all(engine)


def get_session():
    """ Function to get session """
    with Session(engine) as session:
        yield session
