from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.cup_service import get_cup_bracket
from backend.app.services.scorer_service import get_cup_scorers
from backend.app.views.schemas import CupBracketRead

router = APIRouter(prefix="/cup", tags=["cup"])


@router.get("", response_model=CupBracketRead)
def cup_bracket(db: Session = Depends(get_db)) -> dict:
    bracket = get_cup_bracket(db)
    db.commit()
    return bracket


@router.get("/scorers")
def cup_scorers(db: Session = Depends(get_db)) -> list[dict]:
    return get_cup_scorers(db)
