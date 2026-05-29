import matplotlib.pyplot as plt


def plot_race_pace(race_pace, top_n=10):

    pace = race_pace.head(top_n)

    plt.figure(figsize=(10, 6))

    plt.bar(
        pace.index,
        pace.dt.total_seconds()
    )

    plt.title(
        f"Top {top_n} Drivers by Average Race Pace"
    )

    plt.xlabel("Driver")
    plt.ylabel("Average Lap Time (s)")

    plt.grid(
        axis="y",
        linestyle="--",
        alpha=0.5
    )

    plt.tight_layout()

    plt.show()