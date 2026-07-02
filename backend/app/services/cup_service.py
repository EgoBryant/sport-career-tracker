import random

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models import CupTie, CupTournament

USER_TEAM = "Твенте"
ROUND_TITLES = ["1/16 финала", "1/8 финала", "Четвертьфинал", "Полуфинал", "Финал"]
TEAMS = [
    ("MK Dons", 65),
    ("Oxford United", 69),
    ("Port Vale", 64),
    ("Fleetwood Town", 63),
    ("Preston North End", 72),
    ("Wigan Athletic", 68),
    ("Wrexham", 72),
    ("Nottingham Forest", 80),
    ("Cheltenham Town", 62),
    ("Leicester City", 78),
    ("Everton", 78),
    ("Sunderland", 77),
    ("Macclesfield FC", 58),
    ("Crystal Palace", 79),
    ("Wolverhampton Wanderers", 78),
    ("Shrewsbury Town", 62),
    ("Boreham Wood", 57),
    ("Burton Albion", 65),
    (USER_TEAM, 74),
    ("Millwall", 70),
    ("Doncaster Rovers", 64),
    ("Southampton", 75),
    ("Fulham", 79),
    ("Middlesbrough", 73),
    ("Manchester City", 94),
    ("Exeter City", 63),
    ("Newcastle United", 84),
    ("AFC Bournemouth", 79),
    ("Sheffield Wednesday", 67),
    ("Brentford", 80),
    ("Ipswich Town", 78),
    ("Blackpool", 65),
]


def get_cup_bracket(db: Session) -> dict:
    tournament = _current_tournament(db) or _create_tournament(db)
    return _serialize(tournament)


def record_user_cup_result(db: Session, goals_for: int, goals_against: int) -> dict:
    _validate_user_score(goals_for, goals_against)

    tournament = _current_tournament(db)
    if tournament is None or tournament.status != "active":
        if tournament and tournament.status != "abandoned":
            tournament.status = "finished"
        tournament = _create_tournament(db)

    user_tie = _active_user_tie(db, tournament)
    if user_tie is None:
        raise HTTPException(status_code=409, detail="Активная пара Твенте не найдена.")

    round_number = tournament.current_round
    _apply_user_score(user_tie, goals_for, goals_against)
    _simulate_other_ties(db, tournament, round_number)
    stage_advanced = False
    final_won = False

    if user_tie.winner != USER_TEAM:
        tournament.status = "eliminated"
    else:
        stage_advanced = True
        if round_number == len(ROUND_TITLES):
            tournament.status = "champion"
            final_won = True
        else:
            _create_next_round(db, tournament, round_number)
            tournament.current_round += 1

    return {
        "round_number": round_number,
        "stage_advanced": stage_advanced,
        "is_final": round_number == len(ROUND_TITLES),
        "final_won": final_won,
        "bracket": _serialize(tournament),
    }


def _create_tournament(db: Session) -> CupTournament:
    tournament = CupTournament(status="active", current_round=1)
    db.add(tournament)
    db.flush()
    teams = TEAMS.copy()
    random.shuffle(teams)
    for position in range(16):
        home, away = teams[position * 2], teams[position * 2 + 1]
        tournament.ties.append(
            CupTie(
                round_number=1,
                bracket_position=position,
                home_team=home[0],
                away_team=away[0],
                home_strength=home[1],
                away_strength=away[1],
                is_user_tie=USER_TEAM in (home[0], away[0]),
            )
        )
    db.flush()
    return tournament


def _current_tournament(db: Session) -> CupTournament | None:
    return (
        db.query(CupTournament)
        .filter(CupTournament.status != "abandoned")
        .order_by(CupTournament.id.desc())
        .first()
    )


def _active_user_tie(db: Session, tournament: CupTournament) -> CupTie | None:
    return (
        db.query(CupTie)
        .filter(CupTie.tournament_id == tournament.id)
        .filter(CupTie.round_number == tournament.current_round)
        .filter(CupTie.is_user_tie.is_(True))
        .filter(CupTie.is_complete.is_(False))
        .first()
    )


def _validate_user_score(goals_for: int, goals_against: int) -> None:
    target = settings.cup_target_goals
    valid = (
        (goals_for == target and 0 <= goals_against < target)
        or (goals_against == target and 0 <= goals_for < target)
    )
    if not valid:
        raise HTTPException(
            status_code=400,
            detail=f"Кубковый матч заканчивается, когда одна команда забивает {target} гола.",
        )


def _apply_user_score(tie: CupTie, goals_for: int, goals_against: int) -> None:
    if tie.home_team == USER_TEAM:
        tie.home_goals, tie.away_goals = goals_for, goals_against
    else:
        tie.home_goals, tie.away_goals = goals_against, goals_for
    tie.winner = tie.home_team if tie.home_goals > tie.away_goals else tie.away_team
    tie.is_complete = True


def _simulate_other_ties(db: Session, tournament: CupTournament, round_number: int) -> None:
    ties = (
        db.query(CupTie)
        .filter(CupTie.tournament_id == tournament.id)
        .filter(CupTie.round_number == round_number)
        .filter(CupTie.is_user_tie.is_(False))
        .filter(CupTie.is_complete.is_(False))
        .all()
    )
    for tie in ties:
        _simulate_game(tie)


def _simulate_game(tie: CupTie) -> None:
    exponent = (tie.away_strength - tie.home_strength) / settings.cup_strength_divisor
    home_probability = 1 / (1 + 10**exponent)
    home_probability = max(
        settings.cup_win_probability_min,
        min(settings.cup_win_probability_max, home_probability),
    )
    loser_goals = random.randint(0, settings.cup_target_goals - 1)
    if random.random() < home_probability:
        tie.home_goals = settings.cup_target_goals
        tie.away_goals = loser_goals
        tie.winner = tie.home_team
    else:
        tie.home_goals = loser_goals
        tie.away_goals = settings.cup_target_goals
        tie.winner = tie.away_team
    tie.is_complete = True


def _create_next_round(db: Session, tournament: CupTournament, round_number: int) -> None:
    ties = (
        db.query(CupTie)
        .filter(CupTie.tournament_id == tournament.id)
        .filter(CupTie.round_number == round_number)
        .order_by(CupTie.bracket_position)
        .all()
    )
    winners = [(_winner_strength(tie), tie.winner) for tie in ties]
    for position in range(len(winners) // 2):
        home, away = winners[position * 2], winners[position * 2 + 1]
        tournament.ties.append(
            CupTie(
                round_number=round_number + 1,
                bracket_position=position,
                home_team=home[1],
                away_team=away[1],
                home_strength=home[0],
                away_strength=away[0],
                is_user_tie=USER_TEAM in (home[1], away[1]),
            )
        )
    db.flush()


def _winner_strength(tie: CupTie) -> int:
    return tie.home_strength if tie.winner == tie.home_team else tie.away_strength


def _serialize(tournament: CupTournament) -> dict:
    rounds = []
    ties_by_round = {number: [] for number in range(1, 6)}
    for tie in sorted(tournament.ties, key=lambda item: (item.round_number, item.bracket_position)):
        ties_by_round[tie.round_number].append(tie)

    for number, title in enumerate(ROUND_TITLES, start=1):
        ties = ties_by_round[number]
        matches = [_tie_to_dict(tie) for tie in ties]
        if not matches:
            matches = [_placeholder(number, index) for index in range(16 // (2 ** (number - 1)))]
        rounds.append({"key": f"round_{number}", "title": title, "matches": matches})

    return {
        "status": tournament.status,
        "competition": "Кубок Англии",
        "current_round": tournament.current_round,
        "target_goals": settings.cup_target_goals,
        "rounds": rounds,
    }


def _tie_to_dict(tie: CupTie) -> dict:
    return {
        "id": f"tie-{tie.id}",
        "home_team": tie.home_team,
        "away_team": tie.away_team,
        "home_score": tie.home_goals if tie.is_complete else None,
        "away_score": tie.away_goals if tie.is_complete else None,
        "winner": tie.winner,
        "is_user_match": tie.is_user_tie,
    }


def _placeholder(round_number: int, position: int) -> dict:
    return {
        "id": f"placeholder-{round_number}-{position}",
        "home_team": "Победитель пары",
        "away_team": "Победитель пары",
        "home_score": None,
        "away_score": None,
        "winner": None,
        "is_user_match": False,
    }
