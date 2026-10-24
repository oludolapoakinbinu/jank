from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Like, Post
from app.routers.users import get_user, serialize_post
from app.schemas import LikeCreate, PostCreate, PostOut

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostOut, status_code=201)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    author = get_user(db, payload.username)
    post = Post(author_id=author.id, body=payload.body)
    db.add(post)
    db.commit()
    db.refresh(post)
    return serialize_post(db, post)


@router.get("/{post_id}", response_model=PostOut)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    return serialize_post(db, post)


@router.post("/{post_id}/likes", status_code=201)
def like_post(post_id: int, payload: LikeCreate, db: Session = Depends(get_db)):
    user = get_user(db, payload.username)
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    db.add(Like(user_id=user.id, post_id=post.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="already liked")
    return {"post_id": post.id, "username": user.username}


@router.delete("/{post_id}/likes", status_code=204)
def unlike_post(post_id: int, username: str, db: Session = Depends(get_db)):
    user = get_user(db, username)
    like = db.scalar(select(Like).where(Like.user_id == user.id, Like.post_id == post_id))
    if like is None:
        raise HTTPException(status_code=404, detail="like not found")
    db.delete(like)
    db.commit()
