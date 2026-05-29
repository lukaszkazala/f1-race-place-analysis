import fastf1


def load_race_session(
    year: int,
    grand_prix: str,
    session_type: str = "R",
    cache_path: str = "../cache"
):
    """
    Load Formula 1 session using FastF1.
    """

    fastf1.Cache.enable_cache(cache_path)

    session = fastf1.get_session(
        year,
        grand_prix,
        session_type
    )

    session.load()

    return session


def get_laps(session):
    """
    Return laps dataframe.
    """

    return session.laps.copy()