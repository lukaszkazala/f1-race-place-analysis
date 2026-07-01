import pandas as pd


def clean_laps(laps: pd.DataFrame) -> pd.DataFrame:
    """Clean lap data before race pace analysis.

    Args:
        laps: Raw FastF1 lap data.

    Returns:
        Cleaned DataFrame with valid lap times.
    """
    clean_data = laps.copy()

    clean_data = clean_data.pick_quicklaps()
    clean_data = clean_data.dropna(subset=["LapTime", "Driver", "Compound"])

    return clean_data