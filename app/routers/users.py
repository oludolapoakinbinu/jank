from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Follow, Like, Post, User
from app.schemas import FollowCreate, PostOut, UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


def get_user(db: Session, username: str) -> User:
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user


def serialize_post(db: Session, post: Post) -> PostOut:
    like_count = db.scalar(select(func.count()).select_from(Like).where(Like.post_id == post.id)) or 0
    return PostOut(
        id=post.id,
        author=post.author.username,
        body=post.body,
        like_count=like_count,
        created_at=post.created_at,
    )


@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(username=payload.username)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="username taken")
    db.refresh(user)
    return user


@router.get("/{username}", response_model=UserOut)
def read_user(username: str, db: Session = Depends(get_db)):
    return get_user(db, username)


@router.post("/follows", response_model=FollowCreate, status_code=201)
def follow_user(payload: FollowCreate, db: Session = Depends(get_db)):
    if payload.follower == payload.following:
        raise HTTPException(status_code=400, detail="cannot follow yourself")
    follower = get_user(db, payload.follower)
    following = get_user(db, payload.following)
    db.add(Follow(follower_id=follower.id, following_id=following.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="already following")
    return payload


@router.delete("/follows", status_code=204)
def unfollow_user(follower: str, following: str, db: Session = Depends(get_db)):
    follower_user = get_user(db, follower)
    following_user = get_user(db, following)
    follow = db.scalar(
        select(Follow).where(
            Follow.follower_id == follower_user.id,
            Follow.following_id == following_user.id,
        )
    )
    if follow is None:
        raise HTTPException(status_code=404, detail="follow not found")
    db.delete(follow)
    db.commit()


@router.get("/{username}/feed", response_model=list[PostOut])
def read_feed(username: str, db: Session = Depends(get_db)):
    user = get_user(db, username)
    following_ids = list(
        db.scalars(select(Follow.following_id).where(Follow.follower_id == user.id)).all()
    )
    author_ids = following_ids + [user.id]
    posts = db.scalars(
        select(Post).where(Post.author_id.in_(author_ids)).order_by(Post.created_at.desc())
    ).all()
    return [serialize_post(db, post) for post in posts]
