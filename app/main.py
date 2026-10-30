from fastapi import FastAPI
from sqlalchemy import inspect, text

from app.database import engine
from app.models import User
from app.routers import posts, users

User.metadata.create_all(bind=engine)

columns = {column["name"] for column in inspect(engine).get_columns("users")}
with engine.begin() as connection:
    if "display_name" not in columns:
        connection.execute(text("ALTER TABLE users ADD COLUMN display_name VARCHAR(64) NOT NULL DEFAULT ''"))
    if "bio" not in columns:
        connection.execute(text("ALTER TABLE users ADD COLUMN bio VARCHAR(160) NOT NULL DEFAULT ''"))

app = FastAPI()
app.include_router(users.router)
app.include_router(posts.router)
