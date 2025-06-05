import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from urllib.parse import urlparse
import os
import psycopg2

from app.db import Base, get_db
from app.main import app
import os

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

def create_database_if_not_exists(database_url):
    url = urlparse(database_url)
    db_name = url.path[1:]
    admin_url = database_url.replace(f"/{db_name}", "/postgres")

    conn = psycopg2.connect(admin_url)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
    exists = cur.fetchone()
    if not exists:
        cur.execute(f"CREATE DATABASE {db_name}")

create_database_if_not_exists(TEST_DATABASE_URL)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield

    # Teardown: drop the database tables
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
    
@pytest.fixture(autouse=True)
def override_get_db(db_session):
    def _get_db():
        try:
           yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _get_db

    