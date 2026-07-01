import fastf1
import pandas as pd


def load_race_session(
    year: int,
    grand_prix: str,
    session_type: str = "R",
    cache_path: str = "../cache",
):
    """Load a Formula 1 session using the FastF1 library.

    Args:
        year: Championship season.
        grand_prix: Grand Prix name (e.g. "Monaco").
        session_type: Session identifier ("R", "Q", "FP1", etc.).
        cache_path: Directory used to cache downloaded data.

    Returns:
        Loaded FastF1 session object.
    """
    fastf1.Cache.enable_cache(cache_path)

    session = fastf1.get_session(
        year,
        grand_prix,
        session_type,
    )

    session.load()

    return session


def get_laps(session) -> pd.DataFrame:
    """Return a copy of the lap data.

    Args:
        session: Loaded FastF1 session.

    Returns:
        DataFrame containing lap-by-lap information.
    """
    return session.laps.copy()