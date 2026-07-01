import matplotlib.pyplot as plt
import pandas as pd


def plot_race_pace(
    race_pace: pd.Series,
    top_n: int = 10,
    save_path: str | None = None,
) -> None:
    """Plot the top drivers by average race pace.

    Args:
        race_pace: Series with average lap time per driver.
        top_n: Number of fastest drivers to display.
        save_path: Optional path used to save the plot.
    """
    pace = race_pace.head(top_n)
    pace_seconds = pace.dt.total_seconds()

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(
        pace_seconds.index,
        pace_seconds.values,
    )

    ax.set_title(f"Top {top_n} Drivers by Average Race Pace")
    ax.set_xlabel("Driver")
    ax.set_ylabel("Average Lap Time (s)")
    ax.set_ylim(
        pace_seconds.min() - 0.3,
        pace_seconds.max() + 0.3,
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close(fig)


def plot_lap_time_evolution(
    laps: pd.DataFrame,
    drivers: list[str],
    save_path: str | None = None,
) -> None:
    """Plot lap time evolution for selected drivers.

    Args:
        laps: DataFrame containing lap-by-lap race data.
        drivers: List of driver abbreviations to compare.
        save_path: Optional path used to save the plot.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    for driver in drivers:
        driver_laps = (
            laps.pick_drivers(driver)
            .pick_quicklaps()
            .copy()
        )

        ax.plot(
            driver_laps["LapNumber"],
            driver_laps["LapTime"].dt.total_seconds(),
            marker="o",
            linewidth=1.5,
            label=driver,
        )

    ax.set_title("Lap Time Evolution During the Race")
    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time (s)")
    ax.grid(linestyle="--", alpha=0.5)
    ax.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close(fig)