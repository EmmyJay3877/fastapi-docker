
# Ecommerce FastApi server

Welcome to the Ecommerce API Server repository! This project provides a comprehensive API server for an ecommerce platform built using FastAPI and PostgreSQL. With this API server, you can manage products, customers, orders, and more. This README will guide you through setting up and running the API server.


## 🚀 Demo
Swagger UI documentation for the api 👉🏼 https://ecommerce-fastapi-server.onrender.com/docs


## 🧐 Features

- Create, retrieve, update and delete products (only by admin)
- Manage customer information
- Handle order and order history
- Adding and removing products from cart
- Handle payment with stripe
- Payment history in the customer dashboard
- User authentication and authorization
- Password reset and update option


## Prerequisites

Before you begin, ensure you have the following dependencies installed:

- Python (>= 3.6)
- PostgreSQL database

## Tech Stack

**Server:** FastApi

**Database:** PostgreSQL

**ORM:** SQLAlchemy

**Database Migration:** Alembic

**Product Image Management:** Cloudinary

**Payment Service:** Stripe API

**Websocket:** fastapi-socketio



## Installation

Clone the repository

```bash
git clone https://github.com/EmmyJay3877/ecommerce-fastapi-server.git
```
    
Create a virtual environment

```bash
python -m venv venv
```

Activate virtual environment
- On Windows

```bash
venv\Scripts\activate
```

- On macOS and Linux

```bash
source venv/bin/activate
```

Install required dependencies

```bash
pip install -r requirements.txt
```
## Configuration

- Create a postgreSQL database
- Create a Stripe account 
- Create a Cloudinary account 

Set up environment variables:

Create a .env file in the root directory and add the following:

```bash
DATABASE_HOSTNAME=your_database_hostname

DATABASE_PORT=5432

DATABASE_PASSWORD=your_database_password

DATABASE_NAME=your_database_name

DATABASE_USERNAME=your_database_username

SECRET_KEY=your_secret_key

ALGORITHM=your_algorithm_for_jwt

ACCESS_TOKEN_EXPIRE_MINUTES=your_preferred_expiry_time_in_minutes

CLOUD_NAME=your_cloudinary_name

API_KEY=your_cloudinary_api_key

API_SECRET=your_cloudinary_api_secret

SECURE=True

STRIPE_SECRET_KEY=your_stripe_secret_key

LOCAL_CLIENT=http://localhost:3000/

LOCAL_SERVER=http://localhost:8000/

# CLIENT=your_client_production_url

# SERVER=your_server_production_url
```
## Usage

Create required tables on postgreSQL using alembic:

```bash
alembic revision --autogenerate -m "create table"
```

Apply database migrattions:

```bash
alembic upgrade head
```

Run the API server:

```bash
uvicorn app.main:app --reload
```
The API server will be accessible at http://localhost:8000


## Documentation

The API documentation is automatically generated using Swagger UI. You can access it at http://localhost:8000/docs after starting the server. It provides a user-friendly interface to explore and test the various API endpoints.


## Contributing

Contributions are always welcome!

If you find any bugs or want to add new features, feel free to submit a pull request.