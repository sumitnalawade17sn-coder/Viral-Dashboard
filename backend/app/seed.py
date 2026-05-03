from datetime import datetime, timedelta
import random

from .db import Base, SessionLocal, engine
from .models import ContentPost


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(ContentPost).count() > 0:
        print("Sample data already exists. Skipping seed.")
        db.close()
        return

    creators = ["@growwithmaya", "@fitbyleo", "@brandhackdaily", "@creatorops", "@socialpulse"]
    formats = ["Reel", "Carousel", "Static"]
    niches = ["creator economy", "fitness", "personal branding", "ai tools"]
    hashtags = ["#instagramgrowth", "#contentstrategy", "#viralreels", "#creatorbusiness", "#socialmediatips"]
    hooks = [
        "Stop posting like this",
        "3 mistakes killing your reach",
        "Before you post, read this",
        "How to get more saves this week",
        "Unpopular opinion on growth",
    ]
    clusters = ["education", "myth-busting", "case-study", "trend-remix", "behind-the-scenes"]

    now = datetime.utcnow()
    rows = []
    for i in range(120):
        posted_at = now - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
        views = random.randint(8000, 350000)
        likes = int(views * random.uniform(0.02, 0.12))
        comments = random.randint(20, 1600)
        eng = ((likes + comments) / max(views, 1)) * 100
        rows.append(
            ContentPost(
                creator=random.choice(creators),
                content_type=random.choice(formats),
                niche=random.choice(niches),
                hashtag=random.choice(hashtags),
                caption=f"How to improve your results in 7 days. Tip #{random.randint(1,5)} with practical examples.",
                hook=random.choice(hooks),
                topic_cluster=random.choice(clusters),
                views=views,
                likes=likes,
                comments=comments,
                engagement_rate=round(eng, 2),
                posted_at=posted_at,
                link="https://instagram.com/p/placeholder",
            )
        )

    db.add_all(rows)
    db.commit()
    db.close()
    print("Seeded 120 sample posts.")


if __name__ == "__main__":
    seed()
