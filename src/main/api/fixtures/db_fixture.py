from sqlite3 import connect

import pytest
from pygments.styles.dracula import yellow

from src.main.api.db.engine import SessionLocal, engine


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()