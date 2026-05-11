import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event

from app.main import app
from app.REST.data.database import engine, get_db, SessionLocal


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = SessionLocal(bind=connection)
    nested_transaction = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, transaction):
        nonlocal nested_transaction

        if not nested_transaction.is_active:
            nested_transaction = connection.begin_nested()

    try:
        yield session

    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def unique_product_name() -> str:
    return "P" + uuid.uuid4().hex[:9]