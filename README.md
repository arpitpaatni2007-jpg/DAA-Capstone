# Mini-Courier Planner

**Capstone Assignment – Design and Analysis of Algorithms (ETCCDA302)**
K.R. Mangalam University, Gurugram, Haryana

| | |
| --- | --- |
| Student | Arpit Patni (Roll No. 2501730111) |
| Programme | B.Tech Computer Science and Engineering (AI and ML), Section A |
| Faculty | Dr. Shweta Agarwal |
| Language | Python 3.8 or newer |

## About the project

Mini-Courier Planner is a menu-driven Python application that simulates a courier planning system. Given a list of parcels, a road network and a vehicle capacity, it:

1. sorts the parcels by priority and deadline,
2. picks the most valuable set of parcels that fits in the vehicle for one trip,
3. builds the road network as a weighted graph and finds shortest paths,
4. creates an ordered delivery route that starts and ends at the depot,
5. measures and compares the runtime of each major step.

## Algorithms used

| Phase | Algorithm | File |
| --- | --- | --- |
| Phase 2 | Merge Sort (by priority, then deadline) | `sorting.py` |
| Phase 2 | 0/1 Knapsack (Dynamic Programming) | `knapsack.py` |
| Phase 3 | Weighted graph and Dijkstra's algorithm | `graph.py` |
| Phase 3 | Nearest Neighbor TSP approximation | `tsp.py` |
| Phase 4 | Runtime measurement and charts | `performance.py` |

Insertion Sort is also implemented in `sorting.py`, only to compare it with Merge Sort in the performance analysis.

### Time and space complexity

n = parcels, W = vehicle capacity, V = locations, E = roads, k = delivery locations on the route.

| Algorithm | Time | Space |
| --- | --- | --- |
| Merge Sort | O(n log n) | O(n) |
| 0/1 Knapsack (DP) | O(n × W) | O(n × W) |
| Dijkstra (binary heap) | O((V + E) log V) | O(V + E) |
| Distance matrix | O(k × (V + E) log V) | O(k²) |
| Nearest Neighbor TSP | O(k²) | O(k) plus the matrix |

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

Use `python3 main.py` on Linux or macOS. Choose the small or the large dataset, then use the menu:

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

Suggested demo order: 1, 2, 3, 4, 5, 6, 7, 8.
Option 6 needs option 3 first, and option 7 needs options 3 and 6 first.

Other commands:

```
python tests.py          # runs all 47 correctness tests
python performance.py    # runs only the performance analysis
```

## Sample results

| | Small dataset | Large dataset |
| --- | --- | --- |
| Parcels / locations | 12 / 9 | 60 / 21 |
| Vehicle capacity | 30 kg | 120 kg |
| Parcels loaded | 5 (P01, P04, P12, P07, P06) | 28 |
| Total value loaded | Rs 350 | Rs 1755 |
| Route (Nearest Neighbor) | Depot → Dwarka → Uttam Nagar → Vikaspuri → Rajouri Garden → Najafgarh → Depot | 14 stops, returns to Depot |
| Route length | 72 km | 306 km |

**Testing:** `python tests.py` runs 47 checks (sorting, knapsack, Dijkstra, Nearest Neighbor and the full pipeline). All 47 pass. The knapsack is checked against brute force and Dijkstra against Floyd-Warshall.

**Performance** (average of 5 runs, fixed random seed): at n = 4000 parcels Merge Sort takes about 9.6 ms and Insertion Sort about 643.6 ms. Knapsack is the most expensive major step because it fills n × W cells, and Nearest Neighbor time grows with the square of the number of stops. Absolute times depend on the computer.

## Dataset format

Each dataset folder under `data/` has three files:

- `parcels.csv`: `parcel_id, destination, weight, priority, deadline, value`
  weight in kg, priority 1 = highest, deadline in hours, value in Rs
- `roads.csv`: `location_a, location_b, distance`
  distance in km, roads are two-way
- `vehicle.json`: vehicle `capacity` in kg and the name of the `depot`

To test an unseen dataset, create a new folder under `data/` with these three files and change the folder name in `choose_dataset()` in `main.py`. Weights, distances and capacity must be whole numbers. The loader rejects a depot or destination that is not on the map, a negative capacity and a zero or negative weight.

## Folder structure

```
Mini_Courier_Planner/
    main.py              menu-driven application
    data_loader.py       reads the CSV / JSON files and checks the data
    sorting.py           Merge Sort and Insertion Sort
    knapsack.py          0/1 Knapsack using dynamic programming
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
        screenshots/     console output of the application and the tests
    docs/
        PROJECT_REPORT.md   project documentation
```

## Documentation

The complete project documentation (problem definition, algorithms, complexity, sample output, test results, charts and future improvements) is in `docs/PROJECT_REPORT.md`. The formal capstone report is submitted separately.

## Limitations and future work

- The knapsack maximizes value and does not use priority directly; priority only affects the sorting order and the parcel values.
- Nearest Neighbor is a greedy approximation and does not always give the shortest tour.
- Deadlines are used for ordering only; the route does not check that each deadline is met.
- The prototype plans one trip for one vehicle.

Possible improvements: multiple trips and vehicles, 2-opt route improvement, deadline checking against travel time, and real map distances.
