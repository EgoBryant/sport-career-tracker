from calendar import monthrange
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models import Award, AwardType, CardType, GameDay, PlayerProfile


def refresh_cards(db: Session, player: PlayerProfile, as_of: date) -> CardType:
    _clear_awards_for_empty_career(db)
    _deactivate_expired_awards(db, as_of)
    _ensure_totw(db, as_of)
    _ensure_potm(db, player, as_of)
    _ensure_poty(db, player, as_of)

    player.motm_count = _award_count(db, AwardType.MOTM)
    player.totw_count = _award_count(db, AwardType.TOTW)
    player.potm_count = _award_count(db, AwardType.POTM)
    player.poty_count = _award_count(db, AwardType.POTY)
    player.active_card_type = _active_card(db, player, as_of)
    return player.active_card_type


def _clear_awards_for_empty_career(db: Session) -> None:
    if db.query(GameDay.id).first() is None:
        db.query(Award).delete(synchronize_session=False)


def add_motm_award(db: Session, game_day: GameDay) -> None:
    db.add(
        Award(
            award_type=AwardType.MOTM,
            awarded_on=game_day.played_at,
            active_from=game_day.played_at,
            active_until=None,
            title="Player of the Match",
            game_day_id=game_day.id,
        )
    )


def _active_card(db: Session, player: PlayerProfile, as_of: date) -> CardType:
    active_awards = (
        db.query(Award)
        .filter(Award.is_active.is_(True))
        .filter(Award.active_from <= as_of)
        .filter((Award.active_until.is_(None)) | (Award.active_until > as_of))
        .all()
    )
    award_types = {award.award_type for award in active_awards}
    if AwardType.POTY in award_types:
        return CardType.TOTY
    if AwardType.POTM in award_types:
        return CardType.POTM
    if AwardType.TOTW in award_types:
        return CardType.TOTW

    latest_match = (
        db.query(GameDay)
        .filter(GameDay.played_at <= as_of)
        .order_by(GameDay.played_at.desc(), GameDay.id.desc())
        .first()
    )
    if latest_match and latest_match.is_motm:
        return CardType.MOTM
    return _base_card(player.ovr)


def _base_card(ovr: int) -> CardType:
    if ovr < settings.card_silver_ovr_min:
        return CardType.BRONZE
    if ovr < settings.card_gold_ovr_min:
        return CardType.SILVER
    return CardType.GOLD


def _ensure_totw(db: Session, as_of: date) -> None:
    active_week_start = as_of - timedelta(days=as_of.weekday())
    active_week_end = active_week_start + timedelta(days=7)
    source_week_start = active_week_start - timedelta(days=7)
    if _award_exists(db, AwardType.TOTW, active_week_start, active_week_end):
        return

    matches = (
        db.query(GameDay)
        .filter(GameDay.played_at >= source_week_start)
        .filter(GameDay.played_at < active_week_start)
        .all()
    )
    if not matches:
        return

    has_motm = any(match.is_motm for match in matches)
    avg_rating = sum(match.main_rating for match in matches) / len(matches)
    if has_motm or avg_rating > settings.totw_avg_rating_threshold:
        db.add(
            Award(
                award_type=AwardType.TOTW,
                awarded_on=as_of,
                period_start=source_week_start,
                period_end=active_week_start,
                active_from=active_week_start,
                active_until=active_week_end,
                title="Player of the Week",
            )
        )


def _ensure_potm(db: Session, player: PlayerProfile, as_of: date) -> None:
    month_start = as_of.replace(day=1)
    month_end = as_of.replace(day=monthrange(as_of.year, as_of.month)[1])
    next_month = month_end + timedelta(days=1)
    next_month_end = next_month.replace(day=monthrange(next_month.year, next_month.month)[1])
    active_until = next_month_end + timedelta(days=1)
    if _award_exists(db, AwardType.POTM, next_month, active_until):
        return

    matches = (
        db.query(GameDay)
        .filter(GameDay.played_at >= month_start)
        .filter(GameDay.played_at <= month_end)
        .all()
    )
    if len(matches) < settings.potm_min_matches:
        return

    rating_points = sum(match.main_rating for match in matches) * settings.potm_rating_multiplier
    bonuses = sum(settings.potm_motm_bonus for match in matches if match.is_motm)
    bonuses += sum(settings.potm_hat_trick_bonus for match in matches if match.main_goals >= 3)
    bonuses += sum(
        settings.potm_cup_stage_advanced_bonus for match in matches if match.cup_stage_advanced
    )
    bonuses += sum(settings.potm_cup_final_win_bonus for match in matches if match.cup_final_won)
    index = (rating_points + bonuses) / len(matches)
    if index < settings.potm_index_threshold:
        return

    player.market_value = min(
        settings.market_value_max,
        player.market_value + settings.potm_market_bonus,
    )
    db.add(
        Award(
            award_type=AwardType.POTM,
            awarded_on=as_of,
            period_start=month_start,
            period_end=month_end + timedelta(days=1),
            active_from=next_month,
            active_until=active_until,
            title="Player of the Month",
            market_bonus=settings.potm_market_bonus,
        )
    )


def _ensure_poty(db: Session, player: PlayerProfile, as_of: date) -> None:
    year_start = date(as_of.year, 1, 1)
    next_year = date(as_of.year + 1, 1, 1)
    if _award_exists(db, AwardType.POTY, year_start, next_year):
        return

    matches = (
        db.query(GameDay)
        .filter(GameDay.played_at >= year_start)
        .filter(GameDay.played_at < next_year)
        .all()
    )
    if len(matches) < settings.poty_min_matches:
        return

    goals = sum(match.main_goals + match.cup_goals for match in matches)
    final_wins = sum(1 for match in matches if match.cup_final_won)
    avg_rating = sum(match.main_rating for match in matches) / len(matches)
    potm_count = (
        db.query(Award)
        .filter(Award.award_type == AwardType.POTM)
        .filter(Award.awarded_on >= year_start)
        .filter(Award.awarded_on < next_year)
        .count()
    )
    qualifies = (
        goals >= settings.poty_min_goals
        and final_wins >= settings.poty_min_cup_final_wins
        and potm_count >= settings.poty_min_potm_awards
        and avg_rating >= settings.poty_min_avg_rating
    )
    if not qualifies:
        return

    player.market_value = min(
        settings.market_value_max,
        player.market_value + settings.poty_market_bonus,
    )
    db.add(
        Award(
            award_type=AwardType.POTY,
            awarded_on=as_of,
            period_start=year_start,
            period_end=next_year,
            active_from=year_start,
            active_until=next_year,
            title="Player of the Year",
            market_bonus=settings.poty_market_bonus,
        )
    )


def _deactivate_expired_awards(db: Session, as_of: date) -> None:
    db.query(Award).filter(Award.active_until <= as_of).update({"is_active": False})


def _award_exists(db: Session, award_type: AwardType, start: date, end: date) -> bool:
    return (
        db.query(Award)
        .filter(Award.award_type == award_type)
        .filter(Award.active_from == start)
        .filter(Award.active_until == end)
        .first()
        is not None
    )


def _award_count(db: Session, award_type: AwardType) -> int:
    return db.query(func.count(Award.id)).filter(Award.award_type == award_type).scalar() or 0
