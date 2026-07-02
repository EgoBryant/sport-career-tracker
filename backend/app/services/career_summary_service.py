from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models import Award, AwardType, GameDay, MainMatchResult
from backend.app.services.player_service import get_or_create_player
from backend.app.services.trophy_service import (
    EFL_CUP_TROPHY,
    FA_CUP_TROPHY,
    LEAGUE_TROPHY,
    trophy_years,
)


def get_career_summary(db: Session) -> dict:
    player = get_or_create_player(db)
    games = db.query(GameDay).all()
    wins = sum(1 for game in games if game.main_result == MainMatchResult.WIN)
    draws = sum(1 for game in games if game.main_result == MainMatchResult.DRAW)
    losses = sum(1 for game in games if game.main_result == MainMatchResult.LOSS)
    goals = sum(game.main_goals + game.cup_goals for game in games)
    assists = sum(game.main_assists + game.cup_assists for game in games)
    league_title_years = trophy_years(db, LEAGUE_TROPHY)
    cup_win_years = trophy_years(db, FA_CUP_TROPHY)
    efl_cup_years = trophy_years(db, EFL_CUP_TROPHY)
    award_counts = {
        "motm": _award_count(db, AwardType.MOTM),
        "totw": _award_count(db, AwardType.TOTW),
        "potm": _award_count(db, AwardType.POTM),
        "poty": _award_count(db, AwardType.POTY),
    }

    return {
        "energy": "100%",
        "injury": "Здоров",
        "suspension": "Нет",
        "clubs": 1,
        "league_titles": len(league_title_years),
        "league_title_years": league_title_years,
        "cups_won": _cups_won(db),
        "cup_win_years": cup_win_years,
        "current_salary": _salary(
            player.market_value,
            len(league_title_years),
            len(cup_win_years),
            len(efl_cup_years),
            award_counts,
        ),
        "market_value": player.market_value,
        "awards": award_counts,
        "award_dates": {
            "motm": _award_dates(db, AwardType.MOTM),
            "totw": _award_dates(db, AwardType.TOTW),
            "potm": _award_dates(db, AwardType.POTM),
            "poty": _award_dates(db, AwardType.POTY),
        },
        "stats": {
            "app": len(games),
            "w": wins,
            "d": draws,
            "l": losses,
            "g": goals,
            "a": assists,
        },
    }


def _salary(
    market_value: int,
    league_titles: int,
    fa_cups: int,
    efl_cups: int,
    awards: dict[str, int],
) -> int:
    growth = max(0, market_value - settings.initial_market_value)
    steps = growth // settings.salary_market_step
    return (
        settings.salary_base
        + steps * settings.salary_step_bonus
        + league_titles * settings.salary_league_title_bonus
        + fa_cups * settings.salary_fa_cup_bonus
        + efl_cups * settings.salary_efl_cup_bonus
        + awards["motm"] * settings.salary_motm_bonus
        + awards["totw"] * settings.salary_totw_bonus
        + awards["potm"] * settings.salary_potm_bonus
        + awards["poty"] * settings.salary_toty_bonus
    )


def _cups_won(db: Session) -> int:
    return db.query(func.count(GameDay.id)).filter(GameDay.cup_final_won.is_(True)).scalar() or 0


def _award_count(db: Session, award_type: AwardType) -> int:
    return db.query(func.count(Award.id)).filter(Award.award_type == award_type).scalar() or 0


def _award_dates(db: Session, award_type: AwardType) -> list[str]:
    awards = (
        db.query(Award)
        .filter(Award.award_type == award_type)
        .order_by(Award.awarded_on.desc(), Award.id.desc())
        .all()
    )
    return [award.awarded_on.isoformat() for award in awards]
