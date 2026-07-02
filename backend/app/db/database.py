from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.core.config import settings


class Base(DeclarativeBase):
    pass


connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_dev_columns()


def _ensure_dev_columns() -> None:
    migrations = {
        "player_profiles": [
            ("active_card_type", "VARCHAR(8) NOT NULL DEFAULT 'BRONZE'"),
            ("motm_count", "INTEGER NOT NULL DEFAULT 0"),
            ("totw_count", "INTEGER NOT NULL DEFAULT 0"),
            ("potm_count", "INTEGER NOT NULL DEFAULT 0"),
            ("poty_count", "INTEGER NOT NULL DEFAULT 0"),
        ],
        "game_days": [
            ("competition", "VARCHAR(6) NOT NULL DEFAULT 'LEAGUE'"),
            ("team_goals_for", "INTEGER NOT NULL DEFAULT 0"),
            ("team_goals_against", "INTEGER NOT NULL DEFAULT 0"),
            ("market_value_delta", "INTEGER NOT NULL DEFAULT 0"),
            ("active_card_after", "VARCHAR(8) NOT NULL DEFAULT 'BRONZE'"),
        ],
        "awards": [
            ("active_from", "DATE"),
            ("active_until", "DATE"),
            ("is_active", "BOOLEAN NOT NULL DEFAULT 1"),
        ],
        "cup_ties": [
            ("home_goals", "INTEGER NOT NULL DEFAULT 0"),
            ("away_goals", "INTEGER NOT NULL DEFAULT 0"),
        ],
    }
    with engine.begin() as connection:
        for table_name, columns in migrations.items():
            existing = _column_names(connection, table_name)
            for column_name, column_sql in columns:
                if column_name not in existing:
                    connection.execute(
                        text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}")
                    )


def _column_names(connection, table_name: str) -> set[str]:
    rows = connection.execute(text(f"PRAGMA table_info({table_name})")).mappings()
    return {row["name"] for row in rows}
