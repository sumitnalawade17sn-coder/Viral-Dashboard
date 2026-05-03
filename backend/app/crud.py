from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import ContentPost, SavedSearch


def get_dashboard_summary(db: Session):
    total_posts = db.query(func.count(ContentPost.id)).scalar() or 0
    avg_eng = db.query(func.avg(ContentPost.engagement_rate)).scalar() or 0

    fmt = (
        db.query(ContentPost.content_type, func.avg(ContentPost.engagement_rate).label("avg"))
        .group_by(ContentPost.content_type)
        .order_by(func.avg(ContentPost.engagement_rate).desc())
        .first()
    )

    by_hour = (
        db.query(func.strftime("%H:00", ContentPost.posted_at).label("hour"), func.avg(ContentPost.engagement_rate).label("avg"))
        .group_by("hour")
        .order_by(func.avg(ContentPost.engagement_rate).desc())
        .first()
    )

    hooks = [
        h[0]
        for h in db.query(ContentPost.hook, func.avg(ContentPost.engagement_rate).label("avg"))
        .group_by(ContentPost.hook)
        .order_by(func.avg(ContentPost.engagement_rate).desc())
        .limit(5)
        .all()
    ]

    return {
        "total_posts": total_posts,
        "average_engagement_rate": round(float(avg_eng), 2),
        "top_format": fmt[0] if fmt else "N/A",
        "best_posting_time": by_hour[0] if by_hour else "N/A",
        "top_viral_hooks": hooks,
    }


def list_content(
    db: Session,
    hashtag: Optional[str] = None,
    creator: Optional[str] = None,
    content_type: Optional[str] = None,
    min_views: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    query = db.query(ContentPost)
    if hashtag:
        query = query.filter(ContentPost.hashtag == hashtag)
    if creator:
        query = query.filter(ContentPost.creator.ilike(f"%{creator}%"))
    if content_type:
        query = query.filter(ContentPost.content_type == content_type)
    if min_views is not None:
        query = query.filter(ContentPost.views >= min_views)
    if start_date:
        query = query.filter(ContentPost.posted_at >= start_date)
    if end_date:
        query = query.filter(ContentPost.posted_at <= end_date)

    return query.order_by(ContentPost.posted_at.desc()).all()


def get_analysis(db: Session):
    posts = db.query(ContentPost).all()

    hook_counter = Counter([p.hook for p in posts])

    def caption_pattern(caption: str):
        c = caption.lower()
        if "how to" in c:
            return "How-to"
        if "mistake" in c:
            return "Mistake-driven"
        if "before" in c and "after" in c:
            return "Before/After"
        if "3" in c or "5" in c or "7" in c:
            return "Listicle"
        return "Story/Insight"

    pattern_counter = Counter([caption_pattern(p.caption) for p in posts])

    format_perf = defaultdict(list)
    day_perf = defaultdict(list)
    time_perf = defaultdict(list)
    cluster_counter = Counter([p.topic_cluster for p in posts])

    for p in posts:
        format_perf[p.content_type].append(p.engagement_rate)
        day_perf[p.posted_at.strftime("%A")].append(p.engagement_rate)
        time_perf[p.posted_at.strftime("%H:00")].append(p.engagement_rate)

    return {
        "top_hooks": [{"name": k, "count": v} for k, v in hook_counter.most_common(6)],
        "caption_patterns": [{"name": k, "count": v} for k, v in pattern_counter.most_common(6)],
        "best_formats": [
            {"name": k, "engagement": round(sum(v) / len(v), 2)}
            for k, v in sorted(format_perf.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True)
        ],
        "best_posting_days": [
            {"name": k, "engagement": round(sum(v) / len(v), 2)}
            for k, v in sorted(day_perf.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True)
        ],
        "best_posting_times": [
            {"name": k, "engagement": round(sum(v) / len(v), 2)}
            for k, v in sorted(time_perf.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True)
        ],
        "topic_clusters": [{"name": k, "count": v} for k, v in cluster_counter.most_common(8)],
    }


def get_recommendations(db: Session):
    # TODO(INSTAGRAM_API): Replace/augment this with recommendations generated
    # from approved Instagram Graph API ingestion + trend windows.
    base = [
        ("Myth-busting Reel", "Stop doing this in your niche", "Break common misconception", "Hook > 3 myths > CTA save/share"),
        ("Before/After Transformation", "Before you post, watch this", "Show contrast and outcome", "Hook > before > after > steps > CTA"),
        ("3-Step Tutorial", "3 steps to improve results this week", "Tactical quick win", "Hook > steps > proof > CTA"),
        ("Mistake Breakdown", "The #1 mistake creators make", "Problem-awareness angle", "Hook > mistake > fix > CTA"),
        ("Trend Remix", "Everyone is doing this wrong", "React to trend with your method", "Hook > trend clip > commentary > CTA"),
        ("Case Study", "How this post got 10x reach", "Deconstruct winning post", "Hook > context > framework > CTA"),
        ("Hot Take", "Unpopular opinion about growth", "Polarizing but valuable take", "Hook > argument > examples > CTA"),
        ("Checklist Carousel", "Use this checklist before posting", "Save-focused educational", "Slide 1 hook > slides 2-8 tips > CTA"),
        ("Q&A Reel", "Answering your most asked question", "Community-driven content", "Hook > answer > bonus tip > CTA"),
        ("Tool Stack", "5 tools I use every day", "Resource-sharing angle", "Hook > tool list > use cases > CTA"),
    ]
    return [
        {
            "title": t,
            "hook_line": h,
            "caption_angle": c,
            "reel_structure": r,
        }
        for t, h, c, r in base
    ]


def create_search(db: Session, name: str, hashtags: List[str], competitors: List[str], niche: str):
    search = SavedSearch(
        name=name,
        hashtags=",".join(hashtags),
        competitors=",".join(competitors),
        niche=niche,
        created_at=datetime.utcnow(),
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    return search


def list_searches(db: Session):
    return db.query(SavedSearch).order_by(SavedSearch.created_at.desc()).all()
