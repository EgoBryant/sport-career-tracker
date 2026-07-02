import random
from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models import (
    GameDay,
    LeagueMatchResult,
    LeagueRound,
    LeagueTeam,
    MainMatchResult,
)


LEAGUE_TEAMS = [
    ("Арсенал", "ARS", 94),
    ("Манчестер Сити", "MCI", 93),
    ("Манчестер Юнайтед", "MUN", 88),
    ("Астон Вилла", "AVL", 85),
    ("Ливерпуль", "LIV", 87),
    ("Борнмут", "BOU", 76),
    ("Сандерленд", "SUN", 74),
    ("Брайтон", "BHA", 78),
    ("Брентфорд", "BRE", 77),
    ("Челси", "CHE", 80),
    ("Фулхэм", "FUL", 75),
    ("Ньюкасл Юнайтед", "NEW", 79),
    ("Эвертон", "EVE", 73),
    ("Лидс", "LEE", 72),
    ("Кристал Пэлас", "CRY", 71),
    ("Ноттингем Форест", "NFO", 70),
    ("Тоттенхэм", "TOT", 76),
    ("Вест Хэм Юнайтед", "WHU", 69),
    ("Твенте", "TWE", 74),
    ("Вулверхэмптон", "WOL", 66),
]

TWENTE_LOGO_PATH = "assets/images/twente_logo.png"


def ensure_league_teams(db: Session) -> None:
    if db.query(LeagueTeam).count():
        user_team = (
            db.query(LeagueTeam)
            .filter(LeagueTeam.name == settings.league_user_team)
            .first()
        )
        if user_team:
            user_team.logo_url = TWENTE_LOGO_PATH
        return
    reset_league(db)


def reset_league(db: Session) -> list[LeagueTeam]:
    db.query(LeagueMatchResult).delete()
    db.query(LeagueRound).delete()
    db.query(LeagueTeam).delete()
    for name, short_name, strength in LEAGUE_TEAMS:
        logo_url = TWENTE_LOGO_PATH if name == settings.league_user_team else None
        db.add(
            LeagueTeam(
                name=name,
                short_name=short_name,
                logo_url=logo_url,
                strength_rating=strength,
                is_user_team=name == settings.league_user_team,
            )
        )
    db.flush()
    return get_table(db)


def get_table(db: Session) -> list[LeagueTeam]:
    return (
        db.query(LeagueTeam)
        .order_by(
            LeagueTeam.points.desc(),
            LeagueTeam.goal_difference.desc(),
            LeagueTeam.goals_for.desc(),
            LeagueTeam.name.asc(),
        )
        .all()
    )


def simulate_user_round(db: Session, game_day: GameDay) -> None:
    if game_day.played_at.weekday() not in settings.league_round_weekdays:
        raise HTTPException(
            status_code=400,
            detail="Матчи чемпионата можно добавлять только по понедельникам и средам.",
        )

    ensure_league_teams(db)
    user_team = _user_team(db)
    if user_team.played >= settings.league_max_matches:
        raise HTTPException(status_code=400, detail="Сезон чемпионата уже завершен.")

    round_number = user_team.played + 1
    league_round = LeagueRound(
        round_number=round_number,
        played_at=game_day.played_at,
        user_match_id=game_day.id,
    )
    db.add(league_round)
    db.flush()

    opponents = [team for team in db.query(LeagueTeam).all() if team.id != user_team.id]
    opponent = opponents[(round_number - 1) % len(opponents)]
    user_goals = game_day.team_goals_for
    opp_goals = game_day.team_goals_against
    _apply_result(user_team, opponent, user_goals, opp_goals)
    _add_match_result(db, league_round, user_team, opponent, user_goals, opp_goals, True)

    pool = [team for team in opponents if team.id != opponent.id]
    random.Random(game_day.played_at.toordinal()).shuffle(pool)
    for home, away in zip(pool[::2], pool[1::2]):
        home_goals, away_goals = _weighted_score(home, away, game_day.played_at)
        _apply_result(home, away, home_goals, away_goals)
        _add_match_result(db, league_round, home, away, home_goals, away_goals, False)


def _user_team(db: Session) -> LeagueTeam:
    return db.query(LeagueTeam).filter(LeagueTeam.is_user_team.is_(True)).one()

def _weighted_score(home: LeagueTeam, away: LeagueTeam, played_at: date) -> tuple[int, int]:
    rng = random.Random(f"{played_at.isoformat()}-{home.id}-{away.id}")
    diff = home.strength_rating - away.strength_rating
    if rng.random() < settings.league_base_draw_chance:
        goals = max(0, settings.league_goal_base + rng.randint(0, 2))
        return goals, goals

    home_edge = diff + rng.randint(-18, 18)
    if home_edge >= 0:
        return _winner_score(home, away, rng)
    away_goals, home_goals = _winner_score(away, home, rng)
    return home_goals, away_goals


def _winner_score(winner: LeagueTeam, loser: LeagueTeam, rng: random.Random) -> tuple[int, int]:
    strength_gap = max(0, winner.strength_rating - loser.strength_rating)
    goals = settings.league_goal_base + rng.randint(1, 2)
    goals += min(2, strength_gap // settings.league_goal_strength_divisor)
    conceded = rng.randint(0, min(2, goals - 1))
    return goals, conceded


def _apply_result(home: LeagueTeam, away: LeagueTeam, home_goals: int, away_goals: int) -> None:
    home.played += 1
    away.played += 1
    home.goals_for += home_goals
    home.goals_against += away_goals
    away.goals_for += away_goals
    away.goals_against += home_goals
    home.goal_difference = home.goals_for - home.goals_against
    away.goal_difference = away.goals_for - away.goals_against

    if home_goals > away_goals:
        home.wins += 1
        away.losses += 1
        home.points += settings.league_win_points
        away.points += settings.league_loss_points
    elif home_goals < away_goals:
        away.wins += 1
        home.losses += 1
        away.points += settings.league_win_points
        home.points += settings.league_loss_points
    else:
        home.draws += 1
        away.draws += 1
        home.points += settings.league_draw_points
        away.points += settings.league_draw_points


def _add_match_result(
    db: Session,
    league_round: LeagueRound,
    home: LeagueTeam,
    away: LeagueTeam,
    home_goals: int,
    away_goals: int,
    is_user_match: bool,
) -> None:
    result = MainMatchResult.DRAW
    if home_goals > away_goals:
        result = MainMatchResult.WIN
    elif home_goals < away_goals:
        result = MainMatchResult.LOSS
    db.add(
        LeagueMatchResult(
            round_id=league_round.id,
            home_team_id=home.id,
            away_team_id=away.id,
            home_goals=home_goals,
            away_goals=away_goals,
            result=result,
            is_user_match=is_user_match,
        )
    )
