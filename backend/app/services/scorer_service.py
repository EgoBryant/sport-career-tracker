import math

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models import CompetitionType, GameDay, LeagueTeam


SCORERS = (
    ("Эрлинг Холанд", "Манчестер Сити"),
    ("Мохамед Салах", "Ливерпуль"),
    ("Александр Исак", "Ньюкасл Юнайтед"),
    ("Букайо Сака", "Арсенал"),
    ("Олли Уоткинс", "Астон Вилла"),
    ("Коул Палмер", "Челси"),
    ("Бруну Фернандеш", "Манчестер Юнайтед"),
    ("Доминик Соланке", "Тоттенхэм"),
    ("Жоао Педро", "Брайтон"),
    ("Брайан Мбемо", "Брентфорд"),
)


def get_scorers(db: Session) -> list[dict]:
    played = db.query(func.max(LeagueTeam.played)).scalar() or 0
    targets = [int(value) for value in settings.scorer_season_targets.split(",")]
    assist_targets = [int(value) for value in settings.scorer_assist_targets.split(",")]
    rivals = [
        {
            "name": name,
            "club": club,
            "goals": _progressive_goals(target, played),
            "is_user": False,
        }
        for (name, club), target, assist_target in zip(SCORERS, targets, assist_targets)
    ]
    for rival, assist_target in zip(rivals, assist_targets):
        rival["assists"] = _progressive_goals(assist_target, played)
    user_goals = (
        db.query(func.coalesce(func.sum(GameDay.main_goals), 0))
        .filter(GameDay.competition == CompetitionType.LEAGUE)
        .scalar()
    )
    user = {
        "name": "Габов Егор",
        "club": settings.league_user_team,
        "goals": int(user_goals),
        "assists": int(
            db.query(func.coalesce(func.sum(GameDay.main_assists), 0))
            .filter(GameDay.competition == CompetitionType.LEAGUE)
            .scalar()
        ),
        "is_user": True,
    }
    ranked = sorted(
        rivals + [user],
        key=lambda item: (-item["goals"], -item["assists"], item["name"]),
    )
    for index, scorer in enumerate(ranked, 1):
        scorer["position"] = index
    return ranked


def get_cup_scorers(db: Session) -> list[dict]:
    played = db.query(func.count(GameDay.id)).filter(
        GameDay.competition == CompetitionType.CUP
    ).scalar() or 0
    goal_targets = [int(value) for value in settings.cup_scorer_goal_targets.split(",")]
    assist_targets = [int(value) for value in settings.cup_scorer_assist_targets.split(",")]
    rivals = [
        {
            "name": name,
            "club": club,
            "goals": _progress(target, played, settings.cup_scorer_rounds),
            "assists": _progress(assist_target, played, settings.cup_scorer_rounds),
            "is_user": False,
        }
        for (name, club), target, assist_target in zip(
            SCORERS, goal_targets, assist_targets
        )
    ]
    user = {
        "name": "Габов Егор",
        "club": settings.league_user_team,
        "goals": _user_total(db, GameDay.main_goals, CompetitionType.CUP),
        "assists": _user_total(db, GameDay.main_assists, CompetitionType.CUP),
        "is_user": True,
    }
    ranked = sorted(
        rivals + [user],
        key=lambda item: (-item["goals"], -item["assists"], item["name"]),
    )
    for index, scorer in enumerate(ranked, 1):
        scorer["position"] = index
    return ranked


def _progressive_goals(target: int, played: int) -> int:
    if played <= 0:
        return 0
    return min(target, math.ceil(target * played / settings.league_max_matches))


def _progress(target: int, played: int, rounds: int) -> int:
    if played <= 0:
        return 0
    return min(target, math.ceil(target * played / rounds))


def _user_total(db: Session, column, competition: CompetitionType) -> int:
    return int(
        db.query(func.coalesce(func.sum(column), 0))
        .filter(GameDay.competition == competition)
        .scalar()
    )
