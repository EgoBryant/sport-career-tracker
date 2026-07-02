from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.match_service import recent_history

router = APIRouter(tags=["history"])


@router.get("/history")
def history(db: Session = Depends(get_db)) -> list[dict]:
    return recent_history(db)
