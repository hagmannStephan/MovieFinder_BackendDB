from sqlalchemy.orm import Session
from fastapi import Depends
from resources.services.postgresql_service import get_db
from resources.services.auth_service import get_password_hash
import resources.models.postgres as postgers_models
import resources.schemas as schemas
from sqlalchemy.sql import func
from . import group_service
import secrets


def create_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db)
) -> postgers_models.User:
    db_user = db.query(postgers_models.User).filter(postgers_models.User.email == user.email).first()

    # Check if user already exists
    if db_user:
        raise ValueError("Email already registered")
    
    while True:
        friend_code = secrets.token_hex(5)[:5].upper()
        
        if not db.query(postgers_models.User).filter(postgers_models.User.friend_code == friend_code).first():
            break
    
    # Create a new user
    hashed_password = get_password_hash(user.password)
    db_user = postgers_models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        friend_code=friend_code
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_favourites(
        id: int,
        db: Session = Depends(get_db),
) -> list[schemas.Movie]:
    favourite_movies = (
        db.query(postgers_models.Movie)
        .join(postgers_models.user_movies)
        .filter(postgers_models.user_movies.c.user_id == id)
        .all()
    )
    return favourite_movies

def remove_user_favourite(
        id: int,
        movie_id: int,
        db: Session = Depends(get_db)
) -> schemas.Movie:
    user_favourites = get_user_favourites(id, db)
    for movie in user_favourites:
        if movie.movie_id == movie_id:
            db.query(postgers_models.user_movies).filter(
                postgers_models.user_movies.c.user_id == id,
                postgers_models.user_movies.c.movie_id == movie_id
            ).delete()
            db.commit()
            return movie
        
    raise Exception("Movie not found in user's favourites")

def update_user_settings(
        id: int,
        settings: schemas.UserPatchSettings,
        db: Session = Depends(get_db)
) -> schemas.UserPatchSettings:
    user = db.query(postgers_models.User).filter(postgers_models.User.user_id == id).first()
    for key, value in settings.dict().items():
        setattr(user, key, value)
    db.commit()
    return settings
    
def delete_user(
        id: int,
        db: Session = Depends(get_db)
) -> schemas.User:
    user = db.query(postgers_models.User).filter(postgers_models.User.user_id == id).first()

    # Delete user references from related tables
    db.query(postgers_models.user_movies).filter(postgers_models.user_movies.c.user_id == id).delete()
    db.query(postgers_models.group_users).filter(postgers_models.group_users.c.user_id == id).delete()


    # Find groups where the user is admin
    groups = db.query(postgers_models.Group).filter(postgers_models.Group.admin_id == id).all()

    
    for group in groups:
        member_count = db.query(postgers_models.group_users).filter(
            postgers_models.group_users.c.group_id == group.group_id
        ).count()

        if member_count <= 1:
            group_service.delete_group_helper(group.group_id, db)
        else:
            new_admin = db.query(postgers_models.group_users.c.user_id).filter(
                postgers_models.group_users.c.group_id == group.group_id,
                postgers_models.group_users.c.user_id != id  # Exclude the current admin
            ).order_by(func.random()).first()

            if new_admin:
                group.admin_id = new_admin.user_id  # Assign new random admin



    db.delete(user)
    db.commit()
    return user

def get_user_groups(
        id: int,
        db: Session = Depends(get_db)
) -> list[schemas.Group]:
    groups = (
        db.query(postgers_models.Group)
        .join(postgers_models.group_users)
        .filter(postgers_models.group_users.c.user_id == id)
        .all()
    )
    return groups