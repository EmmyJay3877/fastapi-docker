from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings

DATABASE_USERNAME = settings.database_username
DATABASE_PASSWORD = settings.database_password
DATABASE_HOSTNAME = settings.database_hostname
DATABASE_PORT = settings.database_port
DATABASE_NAME = settings.database_name

# format for the connection sring
SQLALCHEMY_DATABASE_URL = f'postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}'

# create engine, its respnsible for the connection of sqlalchemy to postgres
# an engine which the session will use for connection resources
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# talk to the sql database
# these are default values
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# define our base class
Base = declarative_base()  # all our models will be extending this base class

# Dependency, get a session with the db anytime we get a request and close when done


def get_db():
    db = SessionLocal()  # talk with the db
    try:
        yield db
    finally:
        db.close()
