# F1 Race Pace Analysis

## Business Problem

Race pace is one of the most important factors influencing Formula 1 race strategy. Teams continuously analyse lap times to evaluate driver performance, tyre degradation and race consistency.

The objective of this project is to analyse Formula 1 race data and compare driver performance using lap-by-lap telemetry obtained with the FastF1 library.

---

## Project Objectives

- Analyse race pace for each driver
- Compare average lap times
- Identify the fastest race pace
- Measure driver consistency
- Visualize lap time evolution during the race

---

## Dataset

The project uses official Formula 1 timing data downloaded with the **FastF1** library.

Example information includes:

- Driver
- Lap Number
- Lap Time
- Tyre Compound
- Stint
- Position

---

## Analysis Pipeline

```text
FastF1 Session
        │
        ▼
Load Race Data
        │
        ▼
Preprocessing
        │
        ▼
Race Pace Analysis
        │
        ▼
Driver Statistics
        │
        ▼
Visualization
```

---

## Analysis Performed

The project includes:

- Best lap analysis
- Average race pace comparison
- Driver consistency analysis
- Lap-by-lap pace evolution
- Driver performance visualization

---

## Visualizations

The project generates:

- Race pace comparison
- Lap time evolution
- Driver performance charts

---

## Technologies

- Python
- Pandas
- FastF1
- Matplotlib

---

## Repository Structure

```text
f1-race-pace-analysis/
│
├── notebooks/
│   └── f1_analysis.ipynb
│
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── analysis.py
│   └── visualization.py
│
├── README.md
└── requirements.txt
```

---

## Future Improvements

- Qualifying pace analysis
- Tyre degradation modelling
- Pit stop strategy analysis
- Sector time analysis
- Interactive dashboard
- Predictive lap time modelling

---

## About Me

**Łukasz Kazała**

Applied Mathematics – Data Analytics

Interested in:

- Data Science
- Sports Analytics
- Machine Learning
- Quantitative Analysis