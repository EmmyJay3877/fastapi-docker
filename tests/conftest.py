from fastapi.testclient import TestClient
from app.main import app
from app.oauth2 import create_access_token
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.database import get_db
from app.database import Base
import pytest
from app import models

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:boluwatife@localhost:5432/fastapi_test'
# locating our postgres database, using the connection string
# SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}' #format for the connection sring


# create engine, its respnsible for the connection of sqlalchemy to postgres
# an engine which the session will use for connection resources
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# talk to the sql database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # these are default values


# Dependency, get a session with the db anytime we get a request and close when done

@pytest.fixture()
def session():
    # drop tables after tests runs
    Base.metadata.drop_all(bind=engine)
    # create tables before test runs
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal() # talk wiht the db
    try:
        yield db
    finally:
        db.close()    

@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture
def test_user(client):
    user_data = {"email": "hellhu@gmail.com",
    "password": "password123"} 
    res = client.post( "/users/", json=user_data )
    new_user = res.json()
    new_user['password'] = user_data['password']
    assert res.status_code == 201
    return new_user

@pytest.fixture
def test_user2(client):
    user_data = {"email": "hellh23u@gmail.com",
    "password": "password123"} 
    res = client.post( "/users/", json=user_data )
    new_user = res.json()
    new_user['password'] = user_data['password']
    assert res.status_code == 201
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})

@pytest.fixture
def authorized_client(client, token):
    # spread all the headers and add a new one
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [{
        "title": "first",
        "content": "first content",
        "owner_id": test_user['id']
    },{
        "title": "second",
        "content": "second content",
        "owner_id": test_user['id']
    },{
        "title": "third",
        "content": "third content",
        "owner_id": test_user['id']
    },{
        "title": "third",
        "content": "third content",
        "owner_id": test_user2['id']
    }]

    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)
    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()
    return posts