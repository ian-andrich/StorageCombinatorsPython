import contextlib


import sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


@contextlib.contextmanager
def get_engine():
    engine = sqlalchemy.create_engine(
        "postgresql://postgres:example@localhost:8001/postgres"
    )
    connection = engine.connect()
    try:
        yield connection

    finally:
        connection.close()


def test_connection():
    with get_engine() as conn:
        pass


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
            self.name,
            self.fullname,
            self.nickname,
        )


def test_semantics():
    with get_engine() as conn:
        Base.metadata.create_all(conn)
        ed_user = User(name="ed", fullname="Ed Jones", nickname="edsnickname")
