from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .db import Base, engine, get_db

app = FastAPI(title="Viral Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/dashboard/summary", response_model=schemas.DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    return crud.get_dashboard_summary(db)


@app.get("/api/content", response_model=list[schemas.ContentOut])
def content(
    hashtag: Optional[str] = None,
    creator: Optional[str] = None,
    format: Optional[str] = Query(default=None),
    min_views: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    return crud.list_content(db, hashtag, creator, format, min_views, start_date, end_date)


@app.get("/api/analysis", response_model=schemas.AnalysisOut)
def analysis(db: Session = Depends(get_db)):
    return crud.get_analysis(db)


@app.get("/api/recommendations", response_model=list[schemas.RecommendationOut])
def recommendations(db: Session = Depends(get_db)):
    return crud.get_recommendations(db)


@app.post("/api/searches", response_model=schemas.SavedSearchOut)
def save_search(payload: schemas.SavedSearchCreate, db: Session = Depends(get_db)):
    try:
        row = crud.create_search(db, payload.name, payload.hashtags, payload.competitors, payload.niche)
        return {
            "id": row.id,
            "name": row.name,
            "hashtags": row.hashtags.split(",") if row.hashtags else [],
            "competitors": row.competitors.split(",") if row.competitors else [],
            "niche": row.niche,
            "created_at": row.created_at,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not save search: {exc}") from exc


@app.get("/api/searches", response_model=list[schemas.SavedSearchOut])
def get_searches(db: Session = Depends(get_db)):
    rows = crud.list_searches(db)
    return [
        {
            "id": row.id,
            "name": row.name,
            "hashtags": row.hashtags.split(",") if row.hashtags else [],
            "competitors": row.competitors.split(",") if row.competitors else [],
            "niche": row.niche,
            "created_at": row.created_at,
        }
        for row in rows
    ]
