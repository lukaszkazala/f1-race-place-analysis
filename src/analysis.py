import pandas as pd


def get_best_laps(laps):
    """
    Best lap for each driver.
    """

    best_laps = (
        laps
        .pick_quicklaps()
        .groupby("Driver")
        ["LapTime"]
        .min()
        .sort_values()
    )

    return best_laps


def get_average_race_pace(laps):
    """
    Average race pace for each driver.
    """

    race_pace = (
        laps
        .pick_quicklaps()
        .groupby("Driver")
        ["LapTime"]
        .mean()
        .sort_values()
    )

    return race_pace


def get_driver_statistics(laps):
    """
    Calculate average lap time and consistency for each driver
    using representative quick laps only.
    """

    stats = (
        laps
        .pick_quicklaps()
        .groupby("Driver")
        ["LapTime"]
        .agg(
            mean_lap_time="mean",
            lap_time_std="std",
            quick_lap_count="count"
        )
        .sort_values(
            by="mean_lap_time"
        )
    )

    return stats