import pandas as pd


def get_best_laps(laps: pd.DataFrame) -> pd.Series:
    """Calculate the best lap time for each driver.

    Args:
        laps: DataFrame containing lap-by-lap race data.

    Returns:
        Series with the fastest representative lap for each driver.
    """
    best_laps = (
        laps.pick_quicklaps()
        .groupby("Driver")["LapTime"]
        .min()
        .sort_values()
    )

    return best_laps


def get_average_race_pace(laps: pd.DataFrame) -> pd.Series:
    """Calculate average race pace for each driver.

    Args:
        laps: DataFrame containing lap-by-lap race data.

    Returns:
        Series with average representative lap time for each driver.
    """
    race_pace = (
        laps.pick_quicklaps()
        .groupby("Driver")["LapTime"]
        .mean()
        .sort_values()
    )

    return race_pace


def get_driver_statistics(laps: pd.DataFrame) -> pd.DataFrame:
    """Calculate race pace and consistency metrics for each driver.

    Args:
        laps: DataFrame containing lap-by-lap race data.

    Returns:
        DataFrame with average lap time, lap time standard deviation and quick lap count.
    """
    stats = (
        laps.pick_quicklaps()
        .groupby("Driver")["LapTime"]
        .agg(
            mean_lap_time="mean",
            lap_time_std="std",
            quick_lap_count="count",
        )
        .sort_values(by="mean_lap_time")
    )

    return stats