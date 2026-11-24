# Mini-Courier Planner

Capstone Assignment - Design & Analysis of Algorithms (ETCCDA302), K.R. Mangalam University

A menu-driven Python application that simulates a courier planning system. It sorts parcels, picks the best set of parcels for one vehicle trip, builds a road graph, finds shortest paths and creates a delivery route.

| Phase | Algorithm | File |
| --- | --- | --- |
| Phase 2 | Merge Sort (priority, then deadline) | `sorting.py` |
| Phase 2 | 0/1 Knapsack (Dynamic Programming) | `knapsack.py` |
| Phase 3 | Weighted graph + Dijkstra's algorithm | `graph.py` |
| Phase 3 | Nearest Neighbor TSP approximation | `tsp.py` |
| Phase 4 | Runtime measurement and charts | `performance.py` |

## Requirements

- Python 3.8 or newer
- Matplotlib (needed only for the performance charts)

```
pip install matplotlib
```

Everything else uses the Python standard library.

## How to run

Open a terminal inside the project folder and run:

```
python main.py
```

(use `python3 main.py` on Linux/macOS). Choose the small or the large dataset, then use the menu:

```
1. Display all parcels
2. Sort parcels by priority / deadline
3. Select parcels using Knapsack
4. Display the delivery graph
5. Calculate shortest paths using Dijkstra
6. Generate delivery route using Nearest Neighbor TSP
7. Display the final delivery summary
8. Run performance analysis
9. Exit
```

Suggested order for a demo: 1, 2, 3, 4, 5, 6, 7, 8.
Option 6 needs option 3 first, and option 7 needs options 3 and 6 first.

Other commands:

```
python tests.py          runs all correctness tests
python performance.py    runs only the performance analysis
```

## Folder structure

```
Mini_Courier_Planner/
    main.py              menu-driven application
    data_loader.py       reads the CSV / JSON files and checks the data
    sorting.py           merge sort and insertion sort
    knapsack.py          0/1 knapsack using dynamic programming
    graph.py             graph creation and Dijkstra's algorithm
    tsp.py               distance matrix and Nearest Neighbor route
    performance.py       runtime measurement and chart generation
    tests.py             correctness tests
    data/
        small/           12 parcels, 9 locations, capacity 30 kg
        large/           60 parcels, 21 locations, capacity 120 kg
    results/
        runtime_results.csv, performance_output.txt, test_results.txt
        sorting_comparison.png, algorithm_runtimes.png, major_steps_comparison.png
        screenshots/     output traces of the application and tests
    docs/
        PROJECT_REPORT.md   full project documentation
```

## Dataset format

Each dataset folder has three files:

- `parcels.csv` : `parcel_id, destination, weight (kg), priority (1 = highest), deadline (hours), value (Rs)`
- `roads.csv` : `location_a, location_b, distance (km)` - roads are two-way
- `vehicle.json` : vehicle `capacity` in kg and the name of the `depot`

To test an unseen dataset, create a new folder under `data/` with these three files and change the folder name in `choose_dataset()` in `main.py`. Weights, distances and capacity must be whole numbers.

## Documentation

The complete report (problem definition, algorithms, complexity, sample output, test results, charts and future improvements) is in `docs/PROJECT_REPORT.md`.
