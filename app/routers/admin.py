from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2, func
from sqlalchemy.orm import Session
from ..database import get_db
from uuid import uuid4
from typing import List
from datetime import datetime
from jose import JWTError, jwt
from ..func import convert_time
import redis
import json
from ..config import settings
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/admin",  # / = /{id}
    tags=['Admin']  # group requests
)

python_env = settings.python_env

redis_host = settings.redis_host
redis_port = settings.redis_port
redis_username = settings.redis_username
redis_password = settings.redis_password

if python_env == "development":
    redis_client = redis.Redis(host=redis_host, port=redis_port)
else:
    redis_client = redis.Redis(host=redis_host,
                               username=redis_username,
                               password=redis_password,
                               port=redis_port,
                               ssl=True
                               )


@router.get("/", status_code=status.HTTP_200_OK)
def admin_root(db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_user)):
    _notification_count = db.query(models.New_notification_count).first()
    return _notification_count


def update_noti_count(db=None):
    if db is None:
        db = next(get_db())
        _notification_count_query = db.query(models.New_notification_count).filter(
            models.New_notification_count.id == 1)
        existing_notification_count_ = _notification_count_query.first()
        if existing_notification_count_ is None:
            _new_noti = models.New_notification_count(
                _new_notification_count=0)
            db.add(_new_noti)
            db.commit()
            db.refresh(_new_noti)
        else:
            new_count = _notification_count_query.first()._new_notification_count
            new_count += 1
            _notification_count_query.update(
                {"_new_notification_count": new_count}, synchronize_session=False)
            db.commit()
    if db is not None:
        db.close()

    db.close()


@router.get("/notification-reset", status_code=status.HTTP_201_CREATED)
def reset_noti(db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_user)):
    _notification_count_query = db.query(models.New_notification_count).filter(
        models.New_notification_count.id == 1)
    _notification_count_query.update(
        {"_new_notification_count": 0}, synchronize_session=False)
    db.commit()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Response)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    hashed_password = utils.hash(admin.password)
    admin.password = hashed_password
    new_admin = models.Admin(**admin.dict())
    admin_query = db.query(models.Admin).filter((models.Admin.username == admin.username) |
                                                (models.Admin.email == admin.username))
    found_admin = admin_query.first()
    if found_admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Admin already exist.")
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {
        "status": "Registration successfull",
        "data": "Admin has be created"
    }

# verify admin token


@router.get('/check-token', status_code=status.HTTP_200_OK)
def verify_token(token: str = Depends(oauth2.oauth2_scheme)):
    try:
        jwt.decode(token, oauth2.SECRET_KEY, algorithms=[oauth2.ALGORITHM])

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})

# get all notification


@router.get('/notification', status_code=status.HTTP_200_OK)
def get_notification(db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_user)):
    cached_notification = redis_client.get(
        f'notifications?=id{current_admin.id}')
    if cached_notification != None:
        return json.loads(cached_notification)

    notifications = db.query(models.Notificaton).all()
    if not notifications:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"There are no orders")

    _notifications = []
    for notification in notifications:
        formatted_time = func.convert_time(str(notification.created_at))
        _notifications.append(
            {"_notification": notification._notification, "created_at": formatted_time})

    redis_client.setex(f'notifications?=id{current_admin.id}', 30, json.dumps(
        jsonable_encoder(_notifications)))

    return _notifications

# getting all customer orders


@router.get("/orders")
def get_all_orders(db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_user)):
    cached_orders = redis_client.get('all_orders')
    if cached_orders != None:
        return json.loads(cached_orders)

    orders = db.query(models.Order).all()

    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"There are no orders")

    full_orders = []
    for order in orders:
        order_items = db.query(models.OrderItem).filter(
            models.OrderItem.order_id == order.id).all()
        for order_item in order_items:
            item = db.query(models.Item).filter(
                models.Item.id == order_item.item_id).first()
            full_orders.append({
                "order_id": order.id,
                "customer_id": order.customer_id,
                "item_name": item.name,
                "quantity": order_item.quantity,
                "total_price": order_item.total_price,
                "status": order.status,
                "order_date": order.order_date
            })

    if full_orders == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"There are no orders")

    redis_client.setex('all_orders', 30, json.dumps(
        jsonable_encoder(full_orders)))

    return full_orders

# confirm email and reset password


@router.put('/verify', status_code=status.HTTP_200_OK, response_model=schemas.Response)
def check_email(email: schemas.EmailCheck, db: Session = Depends(get_db)):

    admin_query = db.query(models.Admin).filter(
        models.Admin.email == email.email)
    admin = admin_query.first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"This email is not recognized.")

    try:
        new_password = func.generate_code(8)
        hashed_password = utils.hash(new_password)
        password = hashed_password

        admin_query.update({"password": password}, synchronize_session=False)
        db.commit()

        return {
            "status": "ok",
            "data": new_password
        }

    except:
        return {"status": "error"}

# update password


@router.put("/update_password", response_model=schemas.Response)
def update_adminPswrd(password: schemas.PasswordEdit, db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_user)):

    admin_query = db.query(models.Admin).filter(
        models.Admin.id == current_admin.id)
    admin = admin_query.first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Admin was not found.")

    if password.password == '':
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    hashed_password = utils.hash(password.password)
    password = hashed_password
    try:
        admin_query.update({"password": password}, synchronize_session=False)
        db.commit()
        return {
            "status": "ok",
            "data": "Password reset succesfull"
        }
    except:
        return {"status": "error"}


@router.get("/{id}", response_model=schemas.AdminOut)
def get_admins(id: int, db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_user)):
    admin = db.query(models.Admin).filter(models.Admin.id == id).first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Admin with the id: {id} was not found.")

    if admin.id != current_admin.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Not authorized to perform this action")

    return admin
