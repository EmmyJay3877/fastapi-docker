from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import item, customer, auth, order, admin
from .routers.customer import start_background_tasks
from fastapi_socketio import SocketManager
from .routers.admin import update_noti_count
import uvicorn

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customer.router)
app.include_router(order.router)
app.include_router(auth.router)
app.include_router(item.router)
app.include_router(admin.router)

socket_manager = SocketManager(app=app, cors_allowed_origins=[])


@app.get("/")
def root(request: Request, response: Response):
    return "Hello World"


@socket_manager.on('connect')
async def connect(sid, environ, *args):
    print(sid, 'connected')


@socket_manager.on('send_notification')
async def send_noti(sid):

    update_noti_count()
    await socket_manager.emit('receive_notification')


@socket_manager.on('disconnect')
async def disconnect(sid):
    print(sid, 'disconnected')

app.add_event_handler('startup', start_background_tasks)