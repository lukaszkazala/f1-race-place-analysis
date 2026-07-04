import os
from pathlib import Path

import fastf1
import matplotlib.pyplot as plt
import pandas as pd


YEAR = 2026
GRAND_PRIX = "Austria"
SESSION_TYPE = "R"

TOP_N = 5
CACHE_PATH = "cache"
OUTPUT_DIR = Path("images") / "austria_2026"

BACKGROUND_COLOR = "#111111"
TEXT_COLOR = "white"
GRID_COLOR = "white"

TEAM_COLORS = {
    "RUS": "#27F4D2",  # Mercedes
    "ANT": "#27F4D2",
    "VER": "#3671C6",  # Red Bull
    "TSU": "#3671C6",
    "PIA": "#FF8700",  # McLaren
    "NOR": "#FF8700",
    "HAM": "#DC0000",  # Ferrari
    "LEC": "#DC0000",
    "HAD": "#6692FF",  # Racing Bulls
    "LAW": "#6692FF",
    "LIN": "#6692FF",
    "BOR": "#52E252",  # Audi / Sauber style
    "HUL": "#52E252",
    "GAS": "#0090FF",  # Alpine
    "COL": "#0090FF",
    "BEA": "#B6BABD",  # Haas
    "OCO": "#B6BABD",
    "ALB": "#64C4FF",  # Williams
    "SAI": "#64C4FF",
    "ALO": "#006F62",  # Aston Martin
    "STR": "#006F62",
    "PER": "#C8B568",  # Cadillac style placeholder
    "BOT": "#C8B568",
}


def get_driver_color(driver: str) -> str:
    """Return team color for a driver abbreviation."""
    return TEAM_COLORS.get(driver, "#AAAAAA")


def setup_dark_axis(ax) -> None:
    """Apply dark theme styling to a matplotlib axis."""
    ax.set_facecolor(BACKGROUND_COLOR)
    ax.tick_params(colors=TEXT_COLOR)

    for spine in ax.spines.values():
        spine.set_color(TEXT_COLOR)

    ax.grid(
        linestyle="--",
        alpha=0.20,
        color=GRID_COLOR,
    )


def load_race_session(
    year: int,
    grand_prix: str,
    session_type: str,
    cache_path: str,
):
    """Load Formula 1 race session from FastF1."""
    os.makedirs(cache_path, exist_ok=True)
    fastf1.Cache.enable_cache(cache_path)

    session = fastf1.get_session(
        year,
        grand_prix,
        session_type,
    )

    session.load()

    print("\nLoaded session:")
    print(session.event[["EventName", "EventDate", "Country"]])

    return session


def get_official_results(session) -> pd.DataFrame:
    """Extract official race classification from FastF1 session results."""
    results = session.results.copy()

    columns = [
        "Position",
        "Abbreviation",
        "FullName",
        "TeamName",
        "Status",
    ]

    available_columns = [col for col in columns if col in results.columns]
    results = results[available_columns].copy()

    results["Position"] = pd.to_numeric(
        results["Position"],
        errors="coerce",
    )

    results = (
        results
        .dropna(subset=["Position"])
        .sort_values("Position")
        .reset_index(drop=True)
    )

    results["Position"] = results["Position"].astype(int)

    return results


def clean_laps_for_race_pace(laps: pd.DataFrame) -> pd.DataFrame:
    """Clean lap data for representative race pace analysis.

    The function removes non-representative laps such as pit-in/pit-out laps,
    deleted laps, inaccurate laps and extreme lap time outliers.
    """
    clean_laps = laps.copy()

    clean_laps = clean_laps.dropna(
        subset=[
            "Driver",
            "LapTime",
            "LapNumber",
        ]
    )

    if "Deleted" in clean_laps.columns:
        clean_laps = clean_laps[clean_laps["Deleted"] != True]

    if "IsAccurate" in clean_laps.columns:
        clean_laps = clean_laps[clean_laps["IsAccurate"] == True]

    if "PitInTime" in clean_laps.columns:
        clean_laps = clean_laps[clean_laps["PitInTime"].isna()]

    if "PitOutTime" in clean_laps.columns:
        clean_laps = clean_laps[clean_laps["PitOutTime"].isna()]

    clean_laps = clean_laps[clean_laps["LapNumber"] > 1]

    clean_laps["LapTimeSeconds"] = clean_laps["LapTime"].dt.total_seconds()

    clean_laps = clean_laps[
        (clean_laps["LapTimeSeconds"] > 50)
        & (clean_laps["LapTimeSeconds"] < 130)
    ]

    if "TrackStatus" in clean_laps.columns:
        green_flag_laps = clean_laps[
            clean_laps["TrackStatus"].astype(str) == "1"
        ]

        if len(green_flag_laps) >= 0.5 * len(clean_laps):
            clean_laps = green_flag_laps

    clean_laps = remove_driver_outliers(clean_laps)

    return clean_laps


def remove_driver_outliers(laps: pd.DataFrame) -> pd.DataFrame:
    """Remove extreme lap time outliers separately for each driver."""
    cleaned_groups = []

    for _, driver_laps in laps.groupby("Driver"):
        if len(driver_laps) < 8:
            cleaned_groups.append(driver_laps)
            continue

        lower_bound = driver_laps["LapTimeSeconds"].quantile(0.05)
        upper_bound = driver_laps["LapTimeSeconds"].quantile(0.95)

        filtered_laps = driver_laps[
            (driver_laps["LapTimeSeconds"] >= lower_bound)
            & (driver_laps["LapTimeSeconds"] <= upper_bound)
        ]

        cleaned_groups.append(filtered_laps)

    return pd.concat(cleaned_groups, ignore_index=True)


def calculate_race_pace(clean_laps: pd.DataFrame) -> pd.DataFrame:
    """Calculate representative average race pace for each driver."""
    pace = (
        clean_laps
        .groupby("Driver")
        .agg(
            average_lap_time=("LapTimeSeconds", "mean"),
            median_lap_time=("LapTimeSeconds", "median"),
            lap_time_std=("LapTimeSeconds", "std"),
            representative_laps=("LapTimeSeconds", "count"),
        )
        .sort_values("average_lap_time")
        .reset_index()
    )

    fastest_average = pace["average_lap_time"].min()
    pace["gap_to_fastest"] = pace["average_lap_time"] - fastest_average

    return pace


def get_top_finishers(results: pd.DataFrame, top_n: int) -> list[str]:
    """Return driver abbreviations of the top finishers."""
    return (
        results
        .head(top_n)["Abbreviation"]
        .dropna()
        .astype(str)
        .tolist()
    )


def plot_official_result(
    results: pd.DataFrame,
    save_path: Path,
    top_n: int = 10,
) -> None:
    """Plot official top race classification."""
    top_results = results.head(top_n).copy()
    top_results["Label"] = (
        top_results["Position"].astype(str)
        + ". "
        + top_results["Abbreviation"].astype(str)
    )

    colors = [
        get_driver_color(driver)
        for driver in top_results["Abbreviation"]
    ]

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    setup_dark_axis(ax)

    y_positions = range(len(top_results))

    ax.barh(
        y_positions,
        [1] * len(top_results),
        color=colors,
        alpha=0.95,
    )

    ax.set_yticks(y_positions)
    ax.set_yticklabels(top_results["Label"], color=TEXT_COLOR)
    ax.set_xticks([])

    ax.invert_yaxis()

    ax.set_title(
        "Austrian GP 2026 – Official Top 10",
        color=TEXT_COLOR,
        fontsize=18,
        weight="bold",
        pad=15,
    )

    for i, row in top_results.iterrows():
        team = row.get("TeamName", "")
        status = row.get("Status", "")

        ax.text(
            1.03,
            i,
            f"{team} | {status}",
            va="center",
            color=TEXT_COLOR,
            fontsize=10,
        )

    plt.tight_layout()
    plt.savefig(
        save_path,
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.show()
    plt.close(fig)


def plot_race_pace_gap(
    pace: pd.DataFrame,
    save_path: Path,
    top_n: int = 5,
) -> None:
    """Plot gap to fastest average race pace."""
    top_pace = pace.head(top_n).copy()

    colors = [
        get_driver_color(driver)
        for driver in top_pace["Driver"]
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    setup_dark_axis(ax)

    ax.barh(
        top_pace["Driver"],
        top_pace["gap_to_fastest"],
        color=colors,
    )

    ax.invert_yaxis()

    ax.set_title(
        "Austrian GP 2026 – Gap to Fastest Average Race Pace",
        color=TEXT_COLOR,
        fontsize=17,
        weight="bold",
        pad=15,
    )
    ax.set_xlabel("Gap to fastest driver (s/lap)", color=TEXT_COLOR)
    ax.set_ylabel("Driver", color=TEXT_COLOR)

    for index, row in top_pace.iterrows():
        gap = row["gap_to_fastest"]
        average = row["average_lap_time"]

        label = f"+{gap:.3f}s/lap | avg {average:.3f}s"

        if gap == 0:
            label = f"Fastest | avg {average:.3f}s"

        ax.text(
            gap + 0.005,
            index,
            label,
            va="center",
            color=TEXT_COLOR,
            fontsize=10,
        )

    plt.tight_layout()
    plt.savefig(
        save_path,
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.show()
    plt.close(fig)


def plot_lap_time_evolution(
    clean_laps: pd.DataFrame,
    drivers: list[str],
    save_path: Path,
) -> None:
    """Plot rolling lap time evolution for selected drivers."""
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    setup_dark_axis(ax)

    for driver in drivers:
        driver_laps = (
            clean_laps[clean_laps["Driver"] == driver]
            .sort_values("LapNumber")
            .copy()
        )

        if driver_laps.empty:
            continue

        driver_laps["RollingLapTime"] = (
            driver_laps["LapTimeSeconds"]
            .rolling(window=3, min_periods=1)
            .mean()
        )

        ax.plot(
            driver_laps["LapNumber"],
            driver_laps["RollingLapTime"],
            linewidth=3,
            label=driver,
            color=get_driver_color(driver),
        )

    ax.set_title(
        "Austrian GP 2026 – Lap Time Evolution",
        color=TEXT_COLOR,
        fontsize=17,
        weight="bold",
        pad=15,
    )
    ax.set_xlabel("Lap Number", color=TEXT_COLOR)
    ax.set_ylabel("Lap Time – 3 lap rolling average (s)", color=TEXT_COLOR)

    legend = ax.legend(
        facecolor=BACKGROUND_COLOR,
        edgecolor=TEXT_COLOR,
        fontsize=10,
    )

    for text in legend.get_texts():
        text.set_color(TEXT_COLOR)

    plt.tight_layout()
    plt.savefig(
        save_path,
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.show()
    plt.close(fig)


def plot_driver_consistency(
    clean_laps: pd.DataFrame,
    drivers: list[str],
    save_path: Path,
) -> None:
    """Plot lap time distribution for selected drivers."""
    data = []
    labels = []
    colors = []

    for driver in drivers:
        driver_laps = clean_laps[clean_laps["Driver"] == driver]

        if driver_laps.empty:
            continue

        data.append(driver_laps["LapTimeSeconds"])
        labels.append(driver)
        colors.append(get_driver_color(driver))

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    setup_dark_axis(ax)

    box = ax.boxplot(
        data,
        labels=labels,
        patch_artist=True,
        showfliers=False,
    )

    for patch, color in zip(box["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)

    for element in ["whiskers", "caps", "medians"]:
        for item in box[element]:
            item.set_color(TEXT_COLOR)

    ax.set_title(
        "Austrian GP 2026 – Driver Consistency",
        color=TEXT_COLOR,
        fontsize=17,
        weight="bold",
        pad=15,
    )
    ax.set_xlabel("Driver", color=TEXT_COLOR)
    ax.set_ylabel("Representative lap time (s)", color=TEXT_COLOR)

    plt.tight_layout()
    plt.savefig(
        save_path,
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.show()
    plt.close(fig)


def main() -> None:
    """Generate Austrian GP 2026 race performance report."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    session = load_race_session(
        year=YEAR,
        grand_prix=GRAND_PRIX,
        session_type=SESSION_TYPE,
        cache_path=CACHE_PATH,
    )

    results = get_official_results(session)
    laps = session.laps.copy()

    clean_laps = clean_laps_for_race_pace(laps)
    pace = calculate_race_pace(clean_laps)

    top_finishers = get_top_finishers(results, TOP_N)

    if not top_finishers:
        top_finishers = pace.head(TOP_N)["Driver"].tolist()

    print("\nOfficial Top 10:")
    print(results.head(10))

    print("\nRepresentative Race Pace:")
    print(pace.head(10))

    results.to_csv(
        OUTPUT_DIR / "official_results.csv",
        index=False,
    )

    pace.to_csv(
        OUTPUT_DIR / "representative_race_pace.csv",
        index=False,
    )

    plot_official_result(
        results=results,
        save_path=OUTPUT_DIR / "official_top_10.png",
        top_n=10,
    )

    plot_race_pace_gap(
        pace=pace,
        save_path=OUTPUT_DIR / "race_pace_gap_top_5.png",
        top_n=TOP_N,
    )

    plot_lap_time_evolution(
        clean_laps=clean_laps,
        drivers=top_finishers,
        save_path=OUTPUT_DIR / "lap_time_evolution_top_5.png",
    )

    plot_driver_consistency(
        clean_laps=clean_laps,
        drivers=top_finishers,
        save_path=OUTPUT_DIR / "driver_consistency_top_5.png",
    )


if __name__ == "__main__":
    main()