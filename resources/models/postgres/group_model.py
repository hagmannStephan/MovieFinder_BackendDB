from ...services.postgresql_service import Base
from sqlalchemy import (
    Column, Integer, String, Date, JSON, Boolean, CheckConstraint, ForeignKey
)

class Group(Base):
    __tablename__ = "groups"
    group_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(25), nullable=False, index=True)
    admin_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_on = Column(Date, nullable=False, default='now()')

    # Metadata about movie preferences
    show_movies = Column(Boolean, nullable=False, default=True)
    show_tv = Column(Boolean, nullable=False, default=True)
    include_adult = Column(Boolean, nullable=False, default=False)
    language = Column(String(10), nullable=False, default='en-US')
    release_date_gte = Column(Date, nullable=True, default='1900-01-01')
    release_date_lte = Column(Date, nullable=True, default='now()')
    watch_region = Column(String(10), nullable=True, default='CH')
    watch_providers = Column(JSON, nullable=True, default=list)
    with_genres = Column(JSON, nullable=True, default=list)
    without_genres = Column(JSON, nullable=True, default=list)
    

    __table_args__ = (
        CheckConstraint('groups.show_movies = true OR groups.show_tv = true', name='check_at_least_one_true'),
    )