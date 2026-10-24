from fastapi import FastAPI

from app.database import engine
from app.models import User
from app.routers import posts, users

User.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users.router)
app.include_router(posts.router)
