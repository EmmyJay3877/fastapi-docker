from app import schemas
# from .database import client, session
import pytest
from jose import jwt
from app .config import settings


# def test_root(client):
#     res = client.get("/")
#     print(res.json())
#     assert res.json().get('message') == 'Hello World!!!!'
#     assert res.status_code == 200

def test_create_user(client):
    res = client.post("/users/", json={"email": "hell@gmail.com",
    "password": "password123"}) # always add / to your path to avoid status code issess while testing
    new_user = schemas.UserOut(**res.json()) # this will perform a validation
    assert res.status_code == 201

def test_login_user(client, test_user):
    res = client.post("/login", data={"username": test_user['email'],
    "password": test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, 
    settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")
    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ('wrongmail@gmail.com', 'password123', 403),
    ('hellhu@gmail.com', 'wrongpass', 403),
    ('wronguser@gmail.com', 'wrongpass', 403),
    (None, 'password123', 422),
    ('hellhu@gmail.com', None, 422)
])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post("/login", data={"username": email,
     "password": password})
    assert res.status_code == status_code
    # assert res.json().get('detail') == 'Invalid Credentials'

