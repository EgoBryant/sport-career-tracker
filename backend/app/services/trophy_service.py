from datetime import date

from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models import GameDay, LeagueTeam, TeamTrophy

LEAGUE_TROPHY = "league"
FA_CUP_TROPHY = "fa_cup"
EFL_CUP_TROPHY = "efl_cup"


def record_fa_cup(db: Session, won_on: date) -> None:
    _record_once(db, FA_CUP_TROPHY, won_on)


def record_league_if_champion(db: Session, won_on: date) -> None:
    user_team = (
        db.query(LeagueTeam)
        .filter(LeagueTeam.is_user_team.is_(True))
        .first()
    )
    if user_team is None or user_team.played < settings.league_max_matches:
        return

    leader = (
        db.query(LeagueTeam)
        .order_by(
            LeagueTeam.points.desc(),
            LeagueTeam.goal_difference.desc(),
            LeagueTeam.goals_for.desc(),
        )
        .first()
    )
    if leader and leader.id == user_team.id:
        _record_once(db, LEAGUE_TROPHY, won_on)


def trophy_years(db: Session, trophy_type: str) -> list[int]:
    years = {
        row[0]
        for row in db.query(TeamTrophy.won_year)
        .filter(TeamTrophy.trophy_type == trophy_type)
        .all()
    }
    if trophy_type == FA_CUP_TROPHY:
        years.update(
            row[0].year
            for row in db.query(GameDay.played_at)
            .filter(GameDay.cup_final_won.is_(True))
            .all()
        )
    return sorted(years)


def _record_once(db: Session, trophy_type: str, won_on: date) -> None:
    exists = (
        db.query(TeamTrophy.id)
        .filter(TeamTrophy.trophy_type == trophy_type)
        .filter(TeamTrophy.won_year == won_on.year)
        .first()
    )
    if exists is None:
        db.add(
            TeamTrophy(
                trophy_type=trophy_type,
                won_year=won_on.year,
                won_on=won_on,
            )
        )
