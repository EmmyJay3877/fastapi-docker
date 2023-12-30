from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, UploadFile, File
from .. import models, schemas, oauth2
from typing import Optional, List
from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy import func
import cloudinary
import cloudinary.uploader
import requests
from ..config import settings
import redis
import json
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/items", tags=['Items'])

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

CLOUD_NAME = settings.cloud_name
API_KEY = settings.api_key
API_SECRET = settings.api_secret
SECURE = settings.secure

# remember to save this as secrets on the backend before deployment
cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
    secure=SECURE
)

# getting all items


@router.get("/", response_model=List[schemas.Item])
def get_items(db: Session = Depends(get_db)):
    cached_items = redis_client.get('all_items')
    if cached_items != None:
        return json.loads(cached_items)

    items = db.query(models.Item).all()
    all_items = []
    for item in items:
        if item.image != None:
            all_items.append(jsonable_encoder(item))

    redis_client.setex('all_items', 30, json.dumps(all_items))

    return all_items

# create an item


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_user)):

    admin = db.query(models.Admin).filter(
        models.Admin.id == current_admin.id).first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not authorized to perform this action")

    # print(item.name)

    item_query = db.query(models.Item).filter(models.Item.name == item.name)
    invalid_item = item_query.first()

    if invalid_item and invalid_item.image == None:
        item_query.delete(synchronize_session=False)
        db.commit()

    new_item = models.Item(admin_id=current_admin.id, **item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {
        "status": "Almost Done. Please upload an image, else item will not be published.",
        "item_id": new_item.id
    }

# update item image


@router.put("/update_itemImage/{id}", status_code=status.HTTP_201_CREATED)
def upload_itemImage(id: int, image: UploadFile = File(...), db: Session = Depends(get_db),
                     current_admin: int = Depends(oauth2.get_current_user)):
    admin = db.query(models.Admin).filter(
        models.Admin.id == current_admin.id).first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Not authorized to perform this action")

    item_query = db.query(models.Item).filter(models.Item.id == id)
    item = item_query.first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Item with id:{id} not found")

    filename = image.filename
    extension = filename.split(".")[1]

    if extension not in ['png', 'jpg', 'jpeg', 'webp']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Error")

    try:
        delete = cloudinary.uploader.destroy(item.name)
        data = cloudinary.uploader.upload(image.file, public_id=item.name)

        if not data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"An error has occured.")

        img_url = data.get("url")

        item_query.update({"image": img_url}, synchronize_session=False)

        db.commit()
        return {'status': 'Image uploaded successfully'}
    # if an error occured
    except cloudinary.exceptions.Error as e:

        def delete_item_without_image():
            token = oauth2.create_access_token(data={"admin_id": admin.id})
            url = f'https://ecommerce-fastapi-server.onrender.com/items/{item.id}'
            headers = {"Authorization": f"Bearer {token}"}
            data = {'id': item.id}
            response = requests.delete(url, data=data, headers=headers)

        if item.image == None:
            delete_item_without_image()

        print(e)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An error has occured and image could not be uploaded. Please check your internet connection.")

# retrieve an item


@router.get("/{id}", response_model=schemas.Item)
def get_item(id: int, db: Session = Depends(get_db)):
    cached_item = redis_client.get(f"item?id={id}")
    if cached_item != None:
        return json.loads(cached_item)

    item = db.query(models.Item).filter(models.Item.id == id).first()
    redis_client.setex(f"item?id={id}", 30, json.dumps(jsonable_encoder(item)))

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Item with id:{id} not found")

    return item

# deleting an item


@router.delete("/{id}", response_model=schemas.Response)
def delete_item(id: int, db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_user)):
    item_query = db.query(models.Item).filter(models.Item.id == id)
    item = item_query.first()

    if item == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"item with id{id} does not exist")

    if item.admin_id != current_admin.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform this action")

    item_query.delete(synchronize_session=False)
    db.commit()

    return {
        "status": "ok",
        "data": f"Item has been deleted sucessfully"
    }

# update an item


@router.put("/{id}")
def update_item(id: int, updated_item: schemas.ItemCreate, db: Session = Depends(get_db),
                current_admin: int = Depends(oauth2.get_current_user)):
    item_query = db.query(models.Item).filter(models.Item.id == id)
    item = item_query.first()

    if item == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Item with id: {id} does not exist")

    if item.admin_id != current_admin.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform this action")

    item_query.update(updated_item.dict(), synchronize_session=False)

    db.commit()

    return {
        "status": "Item already has an image, you can update image or ignore",
        "item_id": item.id
    }
