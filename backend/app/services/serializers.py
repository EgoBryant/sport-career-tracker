from backend.app.models import GameDay, LeagueTeam, PlayerProfile


def player_to_dict(player: PlayerProfile) -> dict:
    return {
        "ovr": player.ovr,
        "pac": player.pac,
        "sho": player.sho,
        "pas": player.pas,
        "dri": player.dri,
        "def": player.defending,
        "defending": player.defending,
        "phy": player.phy,
        "market_value": player.market_value,
        "active_card_type": player.active_card_type.value,
        "motm_count": player.motm_count,
        "totw_count": player.totw_count,
        "potm_count": player.potm_count,
        "poty_count": player.poty_count,
    }


def game_day_to_dict(game: GameDay) -> dict:
    return {
        "id": game.id,
        "played_at": game.played_at.isoformat(),
        "competition": game.competition.value,
        "main_goals": game.main_goals,
        "main_assists": game.main_assists,
        "team_goals_for": game.team_goals_for,
        "team_goals_against": game.team_goals_against,
        "distance_km": game.distance_km,
        "main_result": game.main_result.value,
        "main_rating": round(game.main_rating, 1),
        "is_motm": game.is_motm,
        "market_value_after": game.market_value_after,
        "active_card_after": game.active_card_after.value,
    }


def league_team_to_dict(team: LeagueTeam, position: int) -> dict:
    return {
        "position": position,
        "name": team.name,
        "short_name": team.short_name,
        "logo_url": team.logo_url,
        "played": team.played,
        "wins": team.wins,
        "draws": team.draws,
        "losses": team.losses,
        "goals_for": team.goals_for,
        "goals_against": team.goals_against,
        "goal_difference": team.goal_difference,
        "points": team.points,
        "is_user_team": team.is_user_team,
    }
