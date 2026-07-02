from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.league_simulation import ensure_league_teams, get_table
from backend.app.services.serializers import league_team_to_dict
from backend.app.services.scorer_service import get_scorers

router = APIRouter(prefix="/league", tags=["league"])


@router.get("/table")
def league_table(db: Session = Depends(get_db)) -> list[dict]:
    ensure_league_teams(db)
    db.commit()
    return [league_team_to_dict(team, index + 1) for index, team in enumerate(get_table(db))]


@router.get("/scorers")
def league_scorers(db: Session = Depends(get_db)) -> list[dict]:
    return get_scorers(db)
