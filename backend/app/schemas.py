from datetime import datetime
from typing import List

from pydantic import BaseModel


class SavedSearchCreate(BaseModel):
    name: str
    hashtags: List[str]
    competitors: List[str]
    niche: str


class SavedSearchOut(BaseModel):
    id: int
    name: str
    hashtags: List[str]
    competitors: List[str]
    niche: str
    created_at: datetime


class DashboardSummary(BaseModel):
    total_posts: int
    average_engagement_rate: float
    top_format: str
    best_posting_time: str
    top_viral_hooks: List[str]


class ContentOut(BaseModel):
    id: int
    creator: str
    content_type: str
    niche: str
    hashtag: str
    caption: str
    hook: str
    topic_cluster: str
    views: int
    likes: int
    comments: int
    engagement_rate: float
    posted_at: datetime
    link: str


class AnalysisOut(BaseModel):
    top_hooks: List[dict]
    caption_patterns: List[dict]
    best_formats: List[dict]
    best_posting_days: List[dict]
    best_posting_times: List[dict]
    topic_clusters: List[dict]


class RecommendationOut(BaseModel):
    title: str
    hook_line: str
    caption_angle: str
    reel_structure: str
