from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models import CardType, PlayerProfile


def get_or_create_player(db: Session) -> PlayerProfile:
    player = db.query(PlayerProfile).order_by(PlayerProfile.id.asc()).first()
    if player:
        return player

    player = PlayerProfile(
        ovr=settings.initial_ovr,
        pac=settings.initial_pac,
        sho=settings.initial_sho,
        pas=settings.initial_pas,
        dri=settings.initial_dri,
        defending=settings.initial_def,
        phy=settings.initial_phy,
        market_value=settings.initial_market_value,
        active_card_type=CardType.BRONZE,
    )
    db.add(player)
    db.flush()
    return player
