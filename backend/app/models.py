from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from .db import Base


class ContentPost(Base):
    __tablename__ = "content_posts"

    id = Column(Integer, primary_key=True, index=True)
    creator = Column(String(100), index=True)
    content_type = Column(String(20), index=True)  # Reel | Carousel | Static
    niche = Column(String(100), index=True)
    hashtag = Column(String(100), index=True)
    caption = Column(Text)
    hook = Column(String(240), index=True)
    topic_cluster = Column(String(100), index=True)
    views = Column(Integer)
    likes = Column(Integer)
    comments = Column(Integer)
    engagement_rate = Column(Float)
    posted_at = Column(DateTime, index=True)
    link = Column(String(255))


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, index=True)
    hashtags = Column(Text)  # comma-separated
    competitors = Column(Text)  # comma-separated
    niche = Column(String(100), index=True)
    created_at = Column(DateTime)
