from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

# this file supervises the login process and returns a token
# the fucntions below are also endpoints
router = APIRouter(tags=['Authentication'])

# user requesting a token/ user login
@router.post('/login', response_model=schemas.Token)
def login(credentials: OAuth2PasswordRequestForm=Depends(), db: Session = Depends(database.get_db)):
    admin = db.query(models.Admin).filter(models.Admin.email==credentials.username).first()
    customer = db.query(models.Customer).filter(models.Customer.email==credentials.username).first()

    if not admin and not customer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if admin:
        if not utils.verify(credentials.password, admin.password): 
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
        else:
            access_token = oauth2.create_access_token(data = {"admin_id": admin.id})
            return {"access_token": access_token, "token_type": "bearer"}
    elif customer:
        if not utils.verify(credentials.password, customer.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
        else:
            access_token = oauth2.create_access_token(data = {"customer_id": customer.id})
            return {"access_token": access_token, "token_type": "bearer"}
    else:
        return None
