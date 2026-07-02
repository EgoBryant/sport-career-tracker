from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.match_service import add_match, recent_history
from backend.app.views.schemas import MatchCreate

router = APIRouter(prefix="/match", tags=["match"])


@router.post("/add")
def create_match(payload: MatchCreate, db: Session = Depends(get_db)) -> dict:
    return add_match(db, payload)


@router.get("/history")
def match_history(db: Session = Depends(get_db)) -> list[dict]:
    return recent_history(db)
