from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.card_service import refresh_cards
from backend.app.services.career_summary_service import get_career_summary
from backend.app.services.player_service import get_or_create_player
from backend.app.services.serializers import player_to_dict

router = APIRouter(tags=["player"])


@router.get("/player")
def get_player(db: Session = Depends(get_db)) -> dict:
    player = get_or_create_player(db)
    refresh_cards(db, player, date.today())
    db.commit()
    return player_to_dict(player)


@router.get("/career-summary")
def career_summary(db: Session = Depends(get_db)) -> dict:
    return get_career_summary(db)
