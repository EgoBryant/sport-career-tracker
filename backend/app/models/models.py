from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.database import Base


class MainMatchResult(str, Enum):
    WIN = "win"
    DRAW = "draw"
    LOSS = "loss"


class CupMatchResult(str, Enum):
    WIN = "win"
    LOSS = "loss"


class CompetitionType(str, Enum):
    LEAGUE = "league"
    CUP = "cup"


class AwardType(str, Enum):
    MOTM = "motm"
    TOTW = "totw"
    POTM = "potm"
    POTY = "poty"


class CardType(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    MOTM = "motm"
    TOTW = "totw"
    POTM = "potm"
    TOTY = "toty"


class PlayerProfile(Base):
    __tablename__ = "player_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ovr: Mapped[int] = mapped_column(Integer, nullable=False)
    pac: Mapped[int] = mapped_column(Integer, nullable=False)
    sho: Mapped[int] = mapped_column(Integer, nullable=False)
    pas: Mapped[int] = mapped_column(Integer, nullable=False)
    dri: Mapped[int] = mapped_column(Integer, nullable=False)
    defending: Mapped[int] = mapped_column(Integer, nullable=False)
    phy: Mapped[int] = mapped_column(Integer, nullable=False)
    market_value: Mapped[int] = mapped_column(Integer, nullable=False)
    active_card_type: Mapped[CardType] = mapped_column(
        SqlEnum(CardType, native_enum=False),
        default=CardType.BRONZE,
        nullable=False,
    )
    motm_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    totw_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    potm_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    poty_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    goal_streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    goal_drought_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class GameDay(Base):
    __tablename__ = "game_days"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    played_at: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    competition: Mapped[CompetitionType] = mapped_column(
        SqlEnum(CompetitionType, native_enum=False),
        default=CompetitionType.LEAGUE,
        nullable=False,
    )

    main_goals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    main_assists: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    team_goals_for: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    team_goals_against: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    activity_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    main_result: Mapped[MainMatchResult] = mapped_column(
        SqlEnum(MainMatchResult, native_enum=False),
        nullable=False,
    )
    main_rating: Mapped[float] = mapped_column(Float, nullable=False)
    is_motm: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    cup_goals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cup_assists: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cup_result: Mapped[CupMatchResult] = mapped_column(
        SqlEnum(CupMatchResult, native_enum=False),
        default=CupMatchResult.LOSS,
        nullable=False,
    )
    cup_round: Mapped[str | None] = mapped_column(String(32), nullable=True)
    cup_rating: Mapped[float] = mapped_column(Float, nullable=False)
    cup_stage_advanced: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_cup_final: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cup_final_won: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    market_value_before: Mapped[int] = mapped_column(Integer, nullable=False)
    market_value_after: Mapped[int] = mapped_column(Integer, nullable=False)
    market_value_delta: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_card_after: Mapped[CardType] = mapped_column(
        SqlEnum(CardType, native_enum=False),
        default=CardType.BRONZE,
        nullable=False,
    )

    ovr_after: Mapped[int] = mapped_column(Integer, nullable=False)
    pac_after: Mapped[int] = mapped_column(Integer, nullable=False)
    sho_after: Mapped[int] = mapped_column(Integer, nullable=False)
    pas_after: Mapped[int] = mapped_column(Integer, nullable=False)
    dri_after: Mapped[int] = mapped_column(Integer, nullable=False)
    defending_after: Mapped[int] = mapped_column(Integer, nullable=False)
    phy_after: Mapped[int] = mapped_column(Integer, nullable=False)

    awards: Mapped[list["Award"]] = relationship(
        back_populates="game_day",
        cascade="all, delete-orphan",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class Award(Base):
    __tablename__ = "awards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    award_type: Mapped[AwardType] = mapped_column(
        SqlEnum(AwardType, native_enum=False),
        index=True,
        nullable=False,
    )
    awarded_on: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    market_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    active_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    game_day_id: Mapped[int | None] = mapped_column(
        ForeignKey("game_days.id"),
        nullable=True,
    )
    game_day: Mapped[GameDay | None] = relationship(back_populates="awards")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class LeagueTeam(Base):
    __tablename__ = "league_teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    short_name: Mapped[str] = mapped_column(String(24), nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    strength_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    played: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    draws: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    losses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    goals_for: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    goals_against: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    goal_difference: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_user_team: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class LeagueRound(Base):
    __tablename__ = "league_rounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    round_number: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    played_at: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    user_match_id: Mapped[int | None] = mapped_column(
        ForeignKey("game_days.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    results: Mapped[list["LeagueMatchResult"]] = relationship(
        back_populates="round",
        cascade="all, delete-orphan",
    )


class LeagueMatchResult(Base):
    __tablename__ = "league_match_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("league_rounds.id"))
    home_team_id: Mapped[int] = mapped_column(ForeignKey("league_teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("league_teams.id"))
    home_goals: Mapped[int] = mapped_column(Integer, nullable=False)
    away_goals: Mapped[int] = mapped_column(Integer, nullable=False)
    result: Mapped[MainMatchResult] = mapped_column(
        SqlEnum(MainMatchResult, native_enum=False),
        nullable=False,
    )
    is_user_match: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    round: Mapped[LeagueRound] = relationship(back_populates="results")
    home_team: Mapped[LeagueTeam] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped[LeagueTeam] = relationship(foreign_keys=[away_team_id])


class CupTournament(Base):
    __tablename__ = "cup_tournaments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    current_round: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    ties: Mapped[list["CupTie"]] = relationship(
        back_populates="tournament",
        cascade="all, delete-orphan",
    )


class CupTie(Base):
    __tablename__ = "cup_ties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("cup_tournaments.id"))
    round_number: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    bracket_position: Mapped[int] = mapped_column(Integer, nullable=False)
    home_team: Mapped[str] = mapped_column(String(64), nullable=False)
    away_team: Mapped[str] = mapped_column(String(64), nullable=False)
    home_strength: Mapped[int] = mapped_column(Integer, nullable=False)
    away_strength: Mapped[int] = mapped_column(Integer, nullable=False)
    home_goals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    away_goals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    home_wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    away_wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    winner: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_user_tie: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    tournament: Mapped[CupTournament] = relationship(back_populates="ties")


class TeamTrophy(Base):
    __tablename__ = "team_trophies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trophy_type: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    won_year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    won_on: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
