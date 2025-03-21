from .auth_routes import router as auth_router
from .movie_routes import router as movie_router
from .user_routes import router as user_router
from .group_routes import router as group_router

__all__ = [
    "auth_router",
    "movie_router",
    "user_router",
    "group_router"
]