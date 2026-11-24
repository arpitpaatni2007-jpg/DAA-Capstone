import csv
import os
import random
import time

import matplotlib.pyplot as plt

from sorting import merge_sort, insertion_sort
from knapsack import knapsack
from graph import build_graph, dijkstra
from tsp import nearest_neighbor

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
RESULTS_FOLDER = os.path.join(BASE_FOLDER, "results")

SIZES = [50, 100, 200, 400, 800]
SORT_SIZES = [100, 500, 1000, 2000, 4000]
KNAPSACK_CAPACITY = 500
REPEATS = 5


def make_parcels(n):
    parcels = []
    for i in range(n):
        parcel = {
            "parcel_id": "P" + str(i),
            "destination": "L" + str(random.randint(1, 50)),
            "weight": random.randint(1, 20),
            "priority": random.randint(1, 3),
            "deadline": random.randint(1, 72),
            "value": random.randint(10, 100),
        }
        parcels.append(parcel)
    return parcels


def make_graph(n):
    roads = []
    for i in range(1, n):
        roads.append((str(i), str(random.randint(0, i - 1)), random.randint(1, 20)))
    for i in range(2 * n):
        a = random.randint(0, n - 1)
        b = random.randint(0, n - 1)
        if a != b:
            roads.append((str(a), str(b), random.randint(1, 20)))
    return build_graph(roads)


def make_matrix(n):
    points = []
    for i in range(n):
        points.append((random.randint(0, 1000), random.randint(0, 1000)))
    places = list(range(n))
    matrix = {}
    for a in places:
        matrix[a] = {}
        for b in places:
            dx = points[a][0] - points[b][0]
            dy = points[a][1] - points[b][1]
            matrix[a][b] = int((dx * dx + dy * dy) ** 0.5)
    return places, matrix


def measure(function, *arguments):
    total = 0
    for _ in range(REPEATS):
        start = time.perf_counter()
        function(*arguments)
        end = time.perf_counter()
        total += end - start
    return total / REPEATS * 1000


def run_performance_analysis(results_folder=RESULTS_FOLDER):
    random.seed(42)
    os.makedirs(results_folder, exist_ok=True)

    print()
    print("Running performance analysis (each time is the average of", REPEATS, "runs)")

    merge_times = []
    insertion_times = []
    for n in SORT_SIZES:
        parcels = make_parcels(n)
        merge_times.append(measure(merge_sort, parcels))
        insertion_times.append(measure(insertion_sort, parcels))

    sort_times = []
    knapsack_times = []
    dijkstra_times = []
    tsp_times = []
    for n in SIZES:
        parcels = make_parcels(n)
        sort_times.append(measure(merge_sort, parcels))
        knapsack_times.append(measure(knapsack, parcels, KNAPSACK_CAPACITY))
        graph = make_graph(n)
        dijkstra_times.append(measure(dijkstra, graph, "0"))
        places, matrix = make_matrix(n)
        tsp_times.append(measure(nearest_neighbor, 0, places, matrix))

    print()
    print("Sorting comparison (time in ms)")
    print(f"{'n':>8}{'Merge Sort':>15}{'Insertion Sort':>18}")
    for i in range(len(SORT_SIZES)):
        print(f"{SORT_SIZES[i]:>8}{merge_times[i]:>15.4f}{insertion_times[i]:>18.4f}")

    print()
    print("Major steps (time in ms)")
    print(f"{'n':>8}{'Merge Sort':>14}{'Knapsack':>14}{'Dijkstra':>14}{'NN TSP':>14}")
    for i in range(len(SIZES)):
        print(f"{SIZES[i]:>8}{sort_times[i]:>14.4f}{knapsack_times[i]:>14.4f}{dijkstra_times[i]:>14.4f}{tsp_times[i]:>14.4f}")

    csv_path = os.path.join(results_folder, "runtime_results.csv")
    with open(csv_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["n", "merge_sort_ms", "knapsack_ms", "dijkstra_ms", "nn_tsp_ms"])
        for i in range(len(SIZES)):
            writer.writerow([SIZES[i], round(sort_times[i], 4), round(knapsack_times[i], 4),
                             round(dijkstra_times[i], 4), round(tsp_times[i], 4)])
        writer.writerow([])
        writer.writerow(["n", "merge_sort_ms", "insertion_sort_ms"])
        for i in range(len(SORT_SIZES)):
            writer.writerow([SORT_SIZES[i], round(merge_times[i], 4), round(insertion_times[i], 4)])

    plt.figure(figsize=(7, 4.5))
    plt.plot(SORT_SIZES, merge_times, marker="o", label="Merge Sort")
    plt.plot(SORT_SIZES, insertion_times, marker="s", label="Insertion Sort")
    plt.xlabel("Number of parcels (n)")
    plt.ylabel("Time (ms)")
    plt.title("Sorting: Merge Sort vs Insertion Sort")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_folder, "sorting_comparison.png"), dpi=120)
    plt.close()

    figure, axes = plt.subplots(2, 2, figsize=(10, 7))
    charts = [
        (axes[0][0], sort_times, "Merge Sort", "Parcels (n)"),
        (axes[0][1], knapsack_times, "0/1 Knapsack (capacity " + str(KNAPSACK_CAPACITY) + ")", "Parcels (n)"),
        (axes[1][0], dijkstra_times, "Dijkstra (single source)", "Locations (n)"),
        (axes[1][1], tsp_times, "Nearest Neighbor TSP", "Locations (n)"),
    ]
    for axis, times, title, label in charts:
        axis.plot(SIZES, times, marker="o")
        axis.set_title(title)
        axis.set_xlabel(label)
        axis.set_ylabel("Time (ms)")
        axis.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_folder, "algorithm_runtimes.png"), dpi=120)
    plt.close()

    plt.figure(figsize=(7, 4.5))
    plt.plot(SIZES, sort_times, marker="o", label="Merge Sort")
    plt.plot(SIZES, knapsack_times, marker="s", label="Knapsack")
    plt.plot(SIZES, dijkstra_times, marker="^", label="Dijkstra")
    plt.plot(SIZES, tsp_times, marker="d", label="Nearest Neighbor TSP")
    plt.yscale("log")
    plt.xlabel("Input size (n)")
    plt.ylabel("Time (ms, log scale)")
    plt.title("Comparison of Major Steps")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_folder, "major_steps_comparison.png"), dpi=120)
    plt.close()

    print()
    print("Saved to", results_folder)
    print("  runtime_results.csv")
    print("  sorting_comparison.png")
    print("  algorithm_runtimes.png")
    print("  major_steps_comparison.png")


if __name__ == "__main__":
    run_performance_analysis()
