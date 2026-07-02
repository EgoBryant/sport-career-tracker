from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models import (
    CompetitionType,
    CupMatchResult,
    GameDay,
    MainMatchResult,
    PlayerProfile,
)
from backend.app.services.card_service import add_motm_award, refresh_cards
from backend.app.services.cup_service import get_cup_bracket, record_user_cup_result
from backend.app.services.league_simulation import get_table, simulate_user_round
from backend.app.services.player_service import get_or_create_player
from backend.app.services.serializers import game_day_to_dict, league_team_to_dict, player_to_dict
from backend.app.services.trophy_service import record_fa_cup, record_league_if_champion
from backend.app.views.schemas import MatchCreate


def add_match(db: Session, payload: MatchCreate) -> dict:
    player = get_or_create_player(db)
    if payload.goals > payload.team_goals_for:
        raise HTTPException(
            status_code=400,
            detail="Личные голы игрока не могут превышать голы команды.",
        )
    competition = CompetitionType(payload.competition)
    result = _result_from_score(payload.team_goals_for, payload.team_goals_against)
    cup_progress = (
        record_user_cup_result(
            db,
            payload.team_goals_for,
            payload.team_goals_against,
        )
        if competition == CompetitionType.CUP
        else None
    )
    rating = _main_rating(payload, result)
    is_motm = rating >= settings.main_match_motm_threshold

    before_value = player.market_value
    _update_goal_form(player, payload.goals)
    _update_skills(player, payload, result, rating)
    _update_market_value(player, rating, competition, result)

    game_day = GameDay(
        played_at=payload.played_at,
        competition=competition,
        main_goals=payload.goals,
        main_assists=payload.assists,
        team_goals_for=payload.team_goals_for,
        team_goals_against=payload.team_goals_against,
        distance_km=payload.distance_km,
        activity_minutes=payload.activity_minutes,
        main_result=result,
        main_rating=rating,
        is_motm=is_motm,
        cup_goals=payload.goals if competition == CompetitionType.CUP else 0,
        cup_assists=payload.assists if competition == CompetitionType.CUP else 0,
        cup_result=CupMatchResult.WIN if result == MainMatchResult.WIN else CupMatchResult.LOSS,
        cup_rating=_cup_rating(payload, result) if competition == CompetitionType.CUP else 0,
        cup_stage_advanced=False,
        market_value_before=before_value,
        market_value_after=player.market_value,
        market_value_delta=player.market_value - before_value,
        ovr_after=player.ovr,
        pac_after=player.pac,
        sho_after=player.sho,
        pas_after=player.pas,
        dri_after=player.dri,
        defending_after=player.defending,
        phy_after=player.phy,
    )
    db.add(game_day)
    db.flush()

    if is_motm:
        add_motm_award(db, game_day)
    if competition == CompetitionType.LEAGUE:
        simulate_user_round(db, game_day)
        record_league_if_champion(db, payload.played_at)
    elif competition == CompetitionType.CUP:
        game_day.cup_round = str(cup_progress["round_number"])
        game_day.cup_stage_advanced = cup_progress["stage_advanced"]
        game_day.is_cup_final = cup_progress["is_final"]
        game_day.cup_final_won = cup_progress["final_won"]
        if cup_progress["final_won"]:
            record_fa_cup(db, payload.played_at)

    game_day.active_card_after = refresh_cards(db, player, payload.played_at)
    db.commit()
    db.refresh(player)
    db.refresh(game_day)

    table = [league_team_to_dict(team, index + 1) for index, team in enumerate(get_table(db))]
    return {
        "player": player_to_dict(player),
        "active_card_type": player.active_card_type.value,
        "market_value": player.market_value,
        "league_table": table,
        "cup_bracket": get_cup_bracket(db),
        "recent_history": recent_history(db),
    }


def recent_history(db: Session, limit: int = 10) -> list[dict]:
    games = (
        db.query(GameDay)
        .order_by(GameDay.played_at.desc(), GameDay.id.desc())
        .limit(limit)
        .all()
    )
    return [game_day_to_dict(game) for game in games]


def _result_from_score(goals_for: int, goals_against: int) -> MainMatchResult:
    if goals_for > goals_against:
        return MainMatchResult.WIN
    if goals_for < goals_against:
        return MainMatchResult.LOSS
    return MainMatchResult.DRAW


def _main_rating(payload: MatchCreate, result: MainMatchResult) -> float:
    rating = settings.main_match_base_rating
    rating += payload.goals * settings.main_match_goal_bonus
    rating += payload.assists * settings.main_match_assist_bonus
    rating += _distance_bonus(payload.distance_km)
    if result == MainMatchResult.WIN:
        rating += settings.main_match_win_bonus
    elif result == MainMatchResult.DRAW:
        rating += settings.main_match_draw_bonus
    else:
        rating += settings.main_match_loss_penalty
    return min(settings.main_match_max_rating, round(rating, 1))


def _cup_rating(payload: MatchCreate, result: MainMatchResult) -> float:
    rating = settings.cup_match_base_rating
    rating += payload.goals * settings.cup_match_goal_bonus
    rating += payload.assists * settings.cup_match_assist_bonus
    rating += (
        settings.cup_match_win_bonus
        if result == MainMatchResult.WIN
        else settings.cup_match_loss_penalty
    )
    return min(settings.main_match_max_rating, round(rating, 1))


def _distance_bonus(distance_km: float) -> float:
    if distance_km >= settings.distance_norm_km + settings.distance_above_norm_delta_km:
        return settings.main_match_distance_above_norm_bonus
    if distance_km >= settings.distance_norm_km:
        return settings.main_match_distance_norm_bonus
    return settings.main_match_distance_below_norm_penalty


def _update_goal_form(player: PlayerProfile, goals: int) -> None:
    if goals > 0:
        player.goal_streak_days += 1
        player.goal_drought_days = 0
    else:
        player.goal_drought_days += 1
        player.goal_streak_days = 0


def _update_market_value(
    player: PlayerProfile,
    rating: float,
    competition: CompetitionType,
    result: MainMatchResult,
) -> None:
    delta = 0
    if rating >= settings.market_main_rating_elite_threshold:
        delta += settings.market_main_rating_elite_bonus
    elif settings.market_main_rating_good_min <= rating <= settings.market_main_rating_good_max:
        delta += settings.market_main_rating_good_bonus
    elif settings.market_main_rating_average_min <= rating <= settings.market_main_rating_average_max:
        delta += settings.market_main_rating_average_bonus
    elif rating <= settings.market_main_rating_poor_max:
        delta += settings.market_main_rating_poor_penalty

    if competition == CompetitionType.CUP:
        delta += (
            settings.market_cup_win_bonus
            if result == MainMatchResult.WIN
            else settings.market_cup_loss_penalty
        )
    if player.goal_streak_days >= settings.goal_streak_min_days:
        delta += settings.goal_streak_market_bonus
    if player.goal_drought_days >= settings.goal_drought_min_days:
        delta += settings.goal_drought_market_penalty
    player.market_value = _clamp(
        player.market_value + delta,
        settings.market_value_min,
        settings.market_value_max,
    )


def _update_skills(
    player: PlayerProfile,
    payload: MatchCreate,
    result: MainMatchResult,
    rating: float,
) -> None:
    if payload.distance_km >= settings.distance_norm_km + settings.distance_above_norm_delta_km:
        player.pac = _skill(player.pac + settings.pac_distance_above_delta)
    elif payload.distance_km < settings.distance_norm_km:
        player.pac = _skill(player.pac + settings.pac_distance_below_delta)

    player.sho = _skill(
        player.sho + payload.goals * settings.sho_per_goal_delta
        if payload.goals
        else player.sho + settings.sho_no_goals_delta
    )
    player.pas = _skill(player.pas + payload.assists * settings.pas_per_assist_delta)
    player.phy = _skill(
        player.phy + settings.phy_active_delta
        if payload.activity_minutes >= settings.activity_minutes_for_phy_bonus
        else player.phy + settings.phy_inactive_delta
    )
    if rating >= settings.main_match_good_rating_threshold:
        player.dri = _skill(player.dri + settings.dri_good_rating_delta)
    if result == MainMatchResult.WIN:
        player.defending = _skill(player.defending + settings.def_main_win_delta)
    elif result == MainMatchResult.LOSS:
        player.defending = _skill(player.defending + settings.def_main_loss_delta)
    player.ovr = _skill(round(
        player.pac * settings.ovr_pac_weight
        + player.sho * settings.ovr_sho_weight
        + player.pas * settings.ovr_pas_weight
        + player.dri * settings.ovr_dri_weight
    ))


def _skill(value: int) -> int:
    return _clamp(value, settings.skill_min, settings.skill_max)


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))
