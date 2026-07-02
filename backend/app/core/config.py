from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(alias="APP_NAME")
    app_version: str = Field(alias="APP_VERSION")
    app_env: str = Field(alias="APP_ENV")
    api_prefix: str = Field(alias="API_PREFIX")
    database_url: str = Field(alias="DATABASE_URL")

    initial_ovr: int = Field(alias="INITIAL_OVR")
    initial_pac: int = Field(alias="INITIAL_PAC")
    initial_sho: int = Field(alias="INITIAL_SHO")
    initial_pas: int = Field(alias="INITIAL_PAS")
    initial_dri: int = Field(alias="INITIAL_DRI")
    initial_def: int = Field(alias="INITIAL_DEF")
    initial_phy: int = Field(alias="INITIAL_PHY")
    initial_market_value: int = Field(alias="INITIAL_MARKET_VALUE")

    skill_min: int = Field(alias="SKILL_MIN")
    skill_max: int = Field(alias="SKILL_MAX")
    market_value_min: int = Field(alias="MARKET_VALUE_MIN")
    market_value_max: int = Field(alias="MARKET_VALUE_MAX")
    card_silver_ovr_min: int = Field(alias="CARD_SILVER_OVR_MIN")
    card_gold_ovr_min: int = Field(alias="CARD_GOLD_OVR_MIN")

    main_match_base_rating: float = Field(alias="MAIN_MATCH_BASE_RATING")
    main_match_goal_bonus: float = Field(alias="MAIN_MATCH_GOAL_BONUS")
    main_match_assist_bonus: float = Field(alias="MAIN_MATCH_ASSIST_BONUS")
    main_match_distance_above_norm_bonus: float = Field(
        alias="MAIN_MATCH_DISTANCE_ABOVE_NORM_BONUS"
    )
    main_match_distance_norm_bonus: float = Field(
        alias="MAIN_MATCH_DISTANCE_NORM_BONUS"
    )
    main_match_distance_below_norm_penalty: float = Field(
        alias="MAIN_MATCH_DISTANCE_BELOW_NORM_PENALTY"
    )
    main_match_win_bonus: float = Field(alias="MAIN_MATCH_WIN_BONUS")
    main_match_draw_bonus: float = Field(alias="MAIN_MATCH_DRAW_BONUS")
    main_match_loss_penalty: float = Field(alias="MAIN_MATCH_LOSS_PENALTY")
    main_match_max_rating: float = Field(alias="MAIN_MATCH_MAX_RATING")
    main_match_motm_threshold: float = Field(alias="MAIN_MATCH_MOTM_THRESHOLD")
    main_match_good_rating_threshold: float = Field(
        alias="MAIN_MATCH_GOOD_RATING_THRESHOLD"
    )
    distance_norm_km: float = Field(alias="DISTANCE_NORM_KM")
    distance_above_norm_delta_km: float = Field(
        alias="DISTANCE_ABOVE_NORM_DELTA_KM"
    )

    cup_match_base_rating: float = Field(alias="CUP_MATCH_BASE_RATING")
    cup_match_goal_bonus: float = Field(alias="CUP_MATCH_GOAL_BONUS")
    cup_match_assist_bonus: float = Field(alias="CUP_MATCH_ASSIST_BONUS")
    cup_match_win_bonus: float = Field(alias="CUP_MATCH_WIN_BONUS")
    cup_match_loss_penalty: float = Field(alias="CUP_MATCH_LOSS_PENALTY")

    market_main_rating_elite_threshold: float = Field(
        alias="MARKET_MAIN_RATING_ELITE_THRESHOLD"
    )
    market_main_rating_elite_bonus: int = Field(
        alias="MARKET_MAIN_RATING_ELITE_BONUS"
    )
    market_main_rating_good_min: float = Field(alias="MARKET_MAIN_RATING_GOOD_MIN")
    market_main_rating_good_max: float = Field(alias="MARKET_MAIN_RATING_GOOD_MAX")
    market_main_rating_good_bonus: int = Field(alias="MARKET_MAIN_RATING_GOOD_BONUS")
    market_main_rating_average_min: float = Field(
        alias="MARKET_MAIN_RATING_AVERAGE_MIN"
    )
    market_main_rating_average_max: float = Field(
        alias="MARKET_MAIN_RATING_AVERAGE_MAX"
    )
    market_main_rating_average_bonus: int = Field(
        alias="MARKET_MAIN_RATING_AVERAGE_BONUS"
    )
    market_main_rating_poor_max: float = Field(alias="MARKET_MAIN_RATING_POOR_MAX")
    market_main_rating_poor_penalty: int = Field(
        alias="MARKET_MAIN_RATING_POOR_PENALTY"
    )
    market_cup_win_bonus: int = Field(alias="MARKET_CUP_WIN_BONUS")
    market_cup_loss_penalty: int = Field(alias="MARKET_CUP_LOSS_PENALTY")
    market_cup_final_win_bonus: int = Field(alias="MARKET_CUP_FINAL_WIN_BONUS")
    goal_streak_min_days: int = Field(alias="GOAL_STREAK_MIN_DAYS")
    goal_streak_market_bonus: int = Field(alias="GOAL_STREAK_MARKET_BONUS")
    goal_drought_min_days: int = Field(alias="GOAL_DROUGHT_MIN_DAYS")
    goal_drought_market_penalty: int = Field(alias="GOAL_DROUGHT_MARKET_PENALTY")

    activity_minutes_for_phy_bonus: int = Field(
        alias="ACTIVITY_MINUTES_FOR_PHY_BONUS"
    )
    pac_distance_above_delta: int = Field(alias="PAC_DISTANCE_ABOVE_DELTA")
    pac_distance_below_delta: int = Field(alias="PAC_DISTANCE_BELOW_DELTA")
    sho_per_goal_delta: int = Field(alias="SHO_PER_GOAL_DELTA")
    sho_no_goals_delta: int = Field(alias="SHO_NO_GOALS_DELTA")
    pas_per_assist_delta: int = Field(alias="PAS_PER_ASSIST_DELTA")
    phy_active_delta: int = Field(alias="PHY_ACTIVE_DELTA")
    phy_inactive_delta: int = Field(alias="PHY_INACTIVE_DELTA")
    dri_good_rating_delta: int = Field(alias="DRI_GOOD_RATING_DELTA")
    def_main_win_delta: int = Field(alias="DEF_MAIN_WIN_DELTA")
    def_cup_win_delta: int = Field(alias="DEF_CUP_WIN_DELTA")
    def_main_loss_delta: int = Field(alias="DEF_MAIN_LOSS_DELTA")
    def_cup_loss_delta: int = Field(alias="DEF_CUP_LOSS_DELTA")

    ovr_pac_weight: float = Field(alias="OVR_PAC_WEIGHT")
    ovr_sho_weight: float = Field(alias="OVR_SHO_WEIGHT")
    ovr_pas_weight: float = Field(alias="OVR_PAS_WEIGHT")
    ovr_dri_weight: float = Field(alias="OVR_DRI_WEIGHT")

    potm_min_matches: int = Field(alias="POTM_MIN_MATCHES")
    potm_rating_multiplier: int = Field(alias="POTM_RATING_MULTIPLIER")
    potm_motm_bonus: int = Field(alias="POTM_MOTM_BONUS")
    potm_hat_trick_bonus: int = Field(alias="POTM_HAT_TRICK_BONUS")
    potm_cup_stage_advanced_bonus: int = Field(
        alias="POTM_CUP_STAGE_ADVANCED_BONUS"
    )
    potm_cup_final_win_bonus: int = Field(alias="POTM_CUP_FINAL_WIN_BONUS")
    potm_index_threshold: int = Field(alias="POTM_INDEX_THRESHOLD")
    potm_market_bonus: int = Field(alias="POTM_MARKET_BONUS")

    poty_min_matches: int = Field(alias="POTY_MIN_MATCHES")
    poty_min_goals: int = Field(alias="POTY_MIN_GOALS")
    poty_min_cup_final_wins: int = Field(alias="POTY_MIN_CUP_FINAL_WINS")
    poty_min_potm_awards: int = Field(alias="POTY_MIN_POTM_AWARDS")
    poty_min_avg_rating: float = Field(alias="POTY_MIN_AVG_RATING")
    poty_market_bonus: int = Field(alias="POTY_MARKET_BONUS")
    totw_avg_rating_threshold: float = Field(alias="TOTW_AVG_RATING_THRESHOLD")

    league_max_matches: int = Field(alias="LEAGUE_MAX_MATCHES")
    league_win_points: int = Field(alias="LEAGUE_WIN_POINTS")
    league_draw_points: int = Field(alias="LEAGUE_DRAW_POINTS")
    league_loss_points: int = Field(alias="LEAGUE_LOSS_POINTS")
    league_user_team: str = Field(alias="LEAGUE_USER_TEAM")
    league_round_days: str = Field(alias="LEAGUE_ROUND_DAYS")
    league_base_draw_chance: float = Field(alias="LEAGUE_BASE_DRAW_CHANCE")
    league_goal_base: int = Field(alias="LEAGUE_GOAL_BASE")
    league_goal_strength_divisor: int = Field(alias="LEAGUE_GOAL_STRENGTH_DIVISOR")
    scorer_season_targets: str = Field(alias="SCORER_SEASON_TARGETS")
    scorer_assist_targets: str = Field(alias="SCORER_ASSIST_TARGETS")

    cup_target_goals: int = Field(alias="CUP_TARGET_GOALS")
    cup_strength_divisor: float = Field(alias="CUP_STRENGTH_DIVISOR")
    cup_win_probability_min: float = Field(alias="CUP_WIN_PROBABILITY_MIN")
    cup_win_probability_max: float = Field(alias="CUP_WIN_PROBABILITY_MAX")
    cup_scorer_goal_targets: str = Field(alias="CUP_SCORER_GOAL_TARGETS")
    cup_scorer_assist_targets: str = Field(alias="CUP_SCORER_ASSIST_TARGETS")
    cup_scorer_rounds: int = Field(alias="CUP_SCORER_ROUNDS")

    salary_base: int = Field(alias="SALARY_BASE")
    salary_market_step: int = Field(alias="SALARY_MARKET_STEP")
    salary_step_bonus: int = Field(alias="SALARY_STEP_BONUS")
    salary_league_title_bonus: int = Field(alias="SALARY_LEAGUE_TITLE_BONUS")
    salary_fa_cup_bonus: int = Field(alias="SALARY_FA_CUP_BONUS")
    salary_efl_cup_bonus: int = Field(alias="SALARY_EFL_CUP_BONUS")
    salary_motm_bonus: int = Field(alias="SALARY_MOTM_BONUS")
    salary_totw_bonus: int = Field(alias="SALARY_TOTW_BONUS")
    salary_potm_bonus: int = Field(alias="SALARY_POTM_BONUS")
    salary_toty_bonus: int = Field(alias="SALARY_TOTY_BONUS")

    @property
    def league_round_weekdays(self) -> set[int]:
        return {int(day.strip()) for day in self.league_round_days.split(",")}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
