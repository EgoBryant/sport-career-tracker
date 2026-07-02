from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MatchCreate(BaseModel):
    played_at: date
    goals: int = Field(ge=0)
    assists: int = Field(ge=0)
    team_goals_for: int = Field(ge=0)
    team_goals_against: int = Field(ge=0)
    distance_km: float = Field(ge=0)
    competition: Literal["league", "cup"] = "league"
    activity_minutes: int = Field(default=90, ge=0)


class PlayerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ovr: int
    pac: int
    sho: int
    pas: int
    dri: int
    defending: int
    phy: int
    market_value: int
    active_card_type: str
    motm_count: int
    totw_count: int
    potm_count: int
    poty_count: int


class GameDayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    played_at: date
    competition: str
    main_goals: int
    main_assists: int
    team_goals_for: int
    team_goals_against: int
    distance_km: float
    main_result: str
    main_rating: float
    is_motm: bool
    market_value_after: int
    active_card_after: str


class LeagueTeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position: int
    name: str
    short_name: str
    logo_url: str | None
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    is_user_team: bool


class MatchAddResponse(BaseModel):
    player: PlayerRead
    active_card_type: str
    market_value: int
    league_table: list[LeagueTeamRead]
    recent_history: list[GameDayRead]


class CupMatchRead(BaseModel):
    id: str
    home_team: str
    away_team: str
    home_score: int | None
    away_score: int | None
    winner: str | None
    is_user_match: bool


class CupRoundRead(BaseModel):
    key: str
    title: str
    matches: list[CupMatchRead]


class CupBracketRead(BaseModel):
    status: str
    competition: str
    current_round: int
    target_goals: int
    rounds: list[CupRoundRead]
