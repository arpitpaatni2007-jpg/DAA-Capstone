import os

from data_loader import load_parcels, load_roads, load_vehicle, check_data
from sorting import merge_sort
from knapsack import knapsack
from graph import build_graph, dijkstra, get_path
from tsp import build_distance_matrix, nearest_neighbor, expand_route
from performance import run_performance_analysis

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))


def choose_dataset():
    print("Choose dataset")
    print("1. Small dataset (12 parcels, 9 locations)")
    print("2. Large dataset (60 parcels, 21 locations)")
    choice = input("Enter 1 or 2: ").strip()
    if choice == "2":
        return "large"
    return "small"


def show_parcels(parcels, title):
    print()
    print(title)
    print("-" * 70)
    print(f"{'ID':<6}{'Destination':<18}{'Weight(kg)':>12}{'Priority':>10}{'Deadline(h)':>13}{'Value(Rs)':>11}")
    print("-" * 70)
    total_weight = 0
    total_value = 0
    for p in parcels:
        print(f"{p['parcel_id']:<6}{p['destination']:<18}{p['weight']:>12}{p['priority']:>10}{p['deadline']:>13}{p['value']:>11}")
        total_weight += p["weight"]
        total_value += p["value"]
    print("-" * 70)
    print("Parcels:", len(parcels), "| Total weight:", total_weight, "kg | Total value: Rs", total_value)


def show_knapsack_table(table, parcels, capacity):
    print()
    if capacity > 40:
        print("DP table has", len(table), "rows and", capacity + 1, "columns (too wide to print).")
        return
    print("DP table (rows = parcels considered, columns = capacity 0 to", str(capacity) + ")")
    print(f"{'':<8}", end="")
    for w in range(capacity + 1):
        print(f"{w:>4}", end="")
    print()
    for i in range(len(table)):
        if i == 0:
            label = "none"
        else:
            label = parcels[i - 1]["parcel_id"]
        print(f"{label:<8}", end="")
        for w in range(capacity + 1):
            print(f"{table[i][w]:>4}", end="")
        print()


def show_graph(graph):
    print()
    print("Delivery graph (adjacency list, distances in km)")
    print("-" * 70)
    road_count = 0
    for place in graph:
        neighbors = []
        for neighbor, distance in graph[place].items():
            neighbors.append(neighbor + " (" + str(distance) + ")")
            road_count += 1
        print(place + " -> " + ", ".join(neighbors))
    print("-" * 70)
    print("Locations:", len(graph), "| Roads:", road_count // 2)


def run_dijkstra(graph, depot):
    places = list(graph.keys())
    print()
    for i in range(len(places)):
        print(str(i + 1) + ".", places[i])
    answer = input("Choose the source location number (press Enter for " + depot + "): ").strip()
    if answer == "":
        source = depot
    elif answer.isdigit() and 1 <= int(answer) <= len(places):
        source = places[int(answer) - 1]
    else:
        print("Invalid location number.")
        return

    distance, previous = dijkstra(graph, source)
    print()
    print("Shortest paths from", source)
    print("-" * 70)
    print(f"{'Destination':<18}{'Distance(km)':>13}   Path")
    print("-" * 70)
    for place in places:
        if place == source:
            continue
        if distance[place] == float("inf"):
            print(f"{place:<18}{'unreachable':>13}")
        else:
            path = get_path(previous, source, place)
            print(f"{place:<18}{distance[place]:>13}   " + " -> ".join(path))


def run_knapsack(sorted_parcels, capacity):
    best_value, selected, table = knapsack(sorted_parcels, capacity)
    show_knapsack_table(table, sorted_parcels, capacity)
    show_parcels(selected, "Selected parcels for this trip")
    total_weight = sum(p["weight"] for p in selected)
    print("Vehicle capacity:", capacity, "kg")
    print("Weight loaded:", total_weight, "kg | Remaining space:", capacity - total_weight, "kg")
    print("Maximum total value (DP table result): Rs", best_value)
    if total_weight <= capacity:
        print("Capacity check: OK")
    else:
        print("Capacity check: FAILED")
    return selected


def run_route(graph, selected, depot):
    destinations = []
    for p in selected:
        if p["destination"] != depot and p["destination"] not in destinations:
            destinations.append(p["destination"])

    matrix = build_distance_matrix(graph, [depot] + destinations)
    route, total_distance = nearest_neighbor(depot, destinations, matrix)
    legs = expand_route(graph, route)

    print()
    print("Delivery route using Nearest Neighbor")
    print("-" * 70)
    print("Locations to visit:", len(destinations))
    print("Route:", " -> ".join(route))
    print()
    for place_from, place_to, distance, path in legs:
        print(f"{place_from} to {place_to}: {distance} km   (road path: {' -> '.join(path)})")
    print()
    print("Total route distance:", total_distance, "km")
    return route, total_distance, legs


def show_summary(selected, not_selected, capacity, depot, route, total_distance, legs):
    total_weight = sum(p["weight"] for p in selected)
    total_value = sum(p["value"] for p in selected)

    print()
    print("=" * 70)
    print("FINAL DELIVERY SUMMARY")
    print("=" * 70)
    print("Depot:", depot)
    print("Vehicle capacity:", capacity, "kg")
    print("Parcels loaded:", len(selected), "| Weight:", total_weight, "kg | Value: Rs", total_value)
    print()
    print(f"{'Stop':<6}{'Location':<18}{'Parcels':<22}{'Leg(km)':>9}{'Total(km)':>11}")
    print("-" * 70)
    covered = 0
    stop_number = 0
    for place_from, place_to, distance, path in legs:
        covered += distance
        if stop_number == len(legs) - 1:
            names = "(return to depot)"
        else:
            ids = [p["parcel_id"] for p in selected if p["destination"] == place_to]
            names = ", ".join(ids)
        stop_number += 1
        print(f"{stop_number:<6}{place_to:<18}{names:<22}{distance:>9}{covered:>11}")
    print("-" * 70)
    print("Route:", " -> ".join(route))
    print("Total route distance:", total_distance, "km")
    left_ids = [p["parcel_id"] for p in not_selected]
    print("Parcels left for the next trip (" + str(len(left_ids)) + "):", ", ".join(left_ids))


def main():
    print("=" * 70)
    print("MINI-COURIER PLANNER")
    print("=" * 70)
    folder = os.path.join(BASE_FOLDER, "data", choose_dataset())

    parcels = load_parcels(os.path.join(folder, "parcels.csv"))
    roads = load_roads(os.path.join(folder, "roads.csv"))
    vehicle = load_vehicle(os.path.join(folder, "vehicle.json"))
    capacity = vehicle["capacity"]
    depot = vehicle["depot"]
    graph = build_graph(roads)
    check_data(parcels, graph, depot, capacity)
    print("Loaded", len(parcels), "parcels,", len(graph), "locations, vehicle capacity", capacity, "kg")

    sorted_parcels = None
    selected = None
    not_selected = None
    route = None
    total_distance = None
    legs = None

    while True:
        print()
        print("-------- MENU --------")
        print("1. Display all parcels")
        print("2. Sort parcels by priority / deadline")
        print("3. Select parcels using Knapsack")
        print("4. Display the delivery graph")
        print("5. Calculate shortest paths using Dijkstra")
        print("6. Generate delivery route using Nearest Neighbor TSP")
        print("7. Display the final delivery summary")
        print("8. Run performance analysis")
        print("9. Exit")
        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            show_parcels(parcels, "All parcels")

        elif choice == "2":
            sorted_parcels = merge_sort(parcels)
            show_parcels(sorted_parcels, "Parcels sorted by priority (1 = highest), then deadline")

        elif choice == "3":
            if sorted_parcels is None:
                sorted_parcels = merge_sort(parcels)
                print("Parcels were sorted first using Merge Sort.")
            selected = run_knapsack(sorted_parcels, capacity)
            not_selected = [p for p in sorted_parcels if p not in selected]
            route = None

        elif choice == "4":
            show_graph(graph)

        elif choice == "5":
            run_dijkstra(graph, depot)

        elif choice == "6":
            if selected is None:
                print("Please run option 3 first to select the parcels.")
            else:
                route, total_distance, legs = run_route(graph, selected, depot)

        elif choice == "7":
            if selected is None:
                print("Please run option 3 first to select the parcels.")
            elif route is None:
                print("Please run option 6 first to generate the route.")
            else:
                show_summary(selected, not_selected, capacity, depot, route, total_distance, legs)

        elif choice == "8":
            run_performance_analysis()

        elif choice == "9":
            print("Thank you for using Mini-Courier Planner.")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 9.")


if __name__ == "__main__":
    main()
