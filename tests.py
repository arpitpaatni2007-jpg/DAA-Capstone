import os
import random
from itertools import combinations, permutations

from data_loader import load_parcels, load_roads, load_vehicle, check_data
from sorting import merge_sort, insertion_sort, get_key
from knapsack import knapsack
from graph import build_graph, dijkstra, get_path, INFINITY
from tsp import build_distance_matrix, nearest_neighbor, expand_route

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

passed = 0
failed = 0


def check(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print("PASS:", name)
    else:
        failed += 1
        print("FAIL:", name)


def random_parcels(n):
    parcels = []
    for i in range(n):
        parcels.append({
            "parcel_id": "P" + str(i),
            "destination": "X",
            "weight": random.randint(1, 10),
            "priority": random.randint(1, 3),
            "deadline": random.randint(1, 50),
            "value": random.randint(1, 100),
        })
    return parcels


def load_dataset(name):
    folder = os.path.join(BASE_FOLDER, "data", name)
    parcels = load_parcels(os.path.join(folder, "parcels.csv"))
    graph = build_graph(load_roads(os.path.join(folder, "roads.csv")))
    vehicle = load_vehicle(os.path.join(folder, "vehicle.json"))
    return parcels, graph, vehicle["capacity"], vehicle["depot"]


def test_sorting():
    print()
    print("--- Sorting tests ---")
    random.seed(1)
    all_match = True
    insertion_match = True
    for size in [2, 5, 10, 50, 200]:
        parcels = random_parcels(size)
        expected = sorted(parcels, key=get_key)
        if merge_sort(parcels) != expected:
            all_match = False
        if insertion_sort(parcels) != expected:
            insertion_match = False
    check("Merge Sort matches Python sorted() on random lists", all_match)
    check("Insertion Sort matches Python sorted() on random lists", insertion_match)
    check("Empty list", merge_sort([]) == [])
    one = [{"parcel_id": "A", "priority": 1, "deadline": 5}]
    check("Single parcel", merge_sort(one) == one)

    same = [{"parcel_id": "A", "priority": 2, "deadline": 5},
            {"parcel_id": "B", "priority": 2, "deadline": 5},
            {"parcel_id": "C", "priority": 2, "deadline": 5}]
    result = merge_sort(same)
    check("Equal keys keep original order (stable)", [p["parcel_id"] for p in result] == ["A", "B", "C"])

    parcels = random_parcels(30)
    before = list(parcels)
    merge_sort(parcels)
    check("Original list is not changed", parcels == before)

    reverse_sorted = sorted(random_parcels(20), key=get_key, reverse=True)
    result = merge_sort(reverse_sorted)
    in_order = all(get_key(result[i]) <= get_key(result[i + 1]) for i in range(len(result) - 1))
    check("Reverse sorted input becomes ordered", in_order)

    parcels, graph, capacity, depot = load_dataset("small")
    result = merge_sort(parcels)
    check("Sample dataset: highest priority first", result[0]["parcel_id"] == "P01" and result[-1]["parcel_id"] == "P03")


def brute_force_best(parcels, capacity):
    best = 0
    for size in range(len(parcels) + 1):
        for group in combinations(parcels, size):
            weight = sum(p["weight"] for p in group)
            value = sum(p["value"] for p in group)
            if weight <= capacity and value > best:
                best = value
    return best


def test_knapsack():
    print()
    print("--- Knapsack tests ---")
    random.seed(2)
    values_match = True
    capacity_ok = True
    value_consistent = True
    for _ in range(40):
        parcels = random_parcels(random.randint(1, 10))
        capacity = random.randint(0, 30)
        best_value, selected, table = knapsack(parcels, capacity)
        if best_value != brute_force_best(parcels, capacity):
            values_match = False
        if sum(p["weight"] for p in selected) > capacity:
            capacity_ok = False
        if sum(p["value"] for p in selected) != best_value:
            value_consistent = False
    check("DP value equals brute force on 40 random cases", values_match)
    check("Selected weight never exceeds capacity (40 random cases)", capacity_ok)
    check("Selected parcels add up to the DP value", value_consistent)

    items = [{"weight": 1, "value": 1}, {"weight": 3, "value": 4}, {"weight": 4, "value": 5}, {"weight": 5, "value": 7}]
    best_value, selected, table = knapsack(items, 7)
    check("Textbook example gives 9", best_value == 9)

    best_value, selected, table = knapsack(random_parcels(5), 0)
    check("Capacity 0 selects nothing", best_value == 0 and selected == [])

    heavy = [{"weight": 50, "value": 100}, {"weight": 60, "value": 90}]
    best_value, selected, table = knapsack(heavy, 10)
    check("All parcels too heavy selects nothing", best_value == 0 and selected == [])

    light = [{"weight": 2, "value": 10}, {"weight": 3, "value": 20}]
    best_value, selected, table = knapsack(light, 100)
    check("All parcels fit, all are selected", best_value == 30 and len(selected) == 2)

    best_value, selected, table = knapsack([], 10)
    check("No parcels", best_value == 0 and selected == [])

    for name in ["small", "large"]:
        parcels, graph, capacity, depot = load_dataset(name)
        best_value, selected, table = knapsack(merge_sort(parcels), capacity)
        total_weight = sum(p["weight"] for p in selected)
        check(name + " dataset: weight " + str(total_weight) + " <= capacity " + str(capacity), total_weight <= capacity)

    parcels, graph, capacity, depot = load_dataset("small")
    best_value, selected, table = knapsack(parcels, capacity)
    check("Small dataset matches brute force (value " + str(best_value) + ")", best_value == brute_force_best(parcels, capacity))


def floyd_warshall(graph):
    places = list(graph.keys())
    dist = {}
    for a in places:
        dist[a] = {}
        for b in places:
            if a == b:
                dist[a][b] = 0
            elif b in graph[a]:
                dist[a][b] = graph[a][b]
            else:
                dist[a][b] = INFINITY
    for k in places:
        for i in places:
            for j in places:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


def random_graph(n):
    roads = []
    for i in range(1, n):
        roads.append((str(i), str(random.randint(0, i - 1)), random.randint(1, 20)))
    for _ in range(n):
        a = random.randint(0, n - 1)
        b = random.randint(0, n - 1)
        if a != b:
            roads.append((str(a), str(b), random.randint(1, 20)))
    return build_graph(roads)


def path_length(graph, path):
    total = 0
    for i in range(len(path) - 1):
        total += graph[path[i]][path[i + 1]]
    return total


def test_dijkstra():
    print()
    print("--- Dijkstra tests ---")
    random.seed(3)
    graph = build_graph([("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 5), ("C", "D", 8)])
    distance, previous = dijkstra(graph, "A")
    check("Hand-checked distances A->B=3, A->C=1, A->D=8",
          distance["B"] == 3 and distance["C"] == 1 and distance["D"] == 8)
    check("Hand-checked path A->D is A, C, B, D", get_path(previous, "A", "D") == ["A", "C", "B", "D"])
    check("Distance to source is 0 and path is just the source", distance["A"] == 0 and get_path(previous, "A", "A") == ["A"])

    matches = True
    paths_ok = True
    for _ in range(15):
        g = random_graph(12)
        reference = floyd_warshall(g)
        for source in g:
            distance, previous = dijkstra(g, source)
            for target in g:
                if distance[target] != reference[source][target]:
                    matches = False
                path = get_path(previous, source, target)
                if path_length(g, path) != distance[target]:
                    paths_ok = False
    check("Dijkstra equals Floyd-Warshall on 15 random graphs (all sources)", matches)
    check("Returned path length equals the reported distance", paths_ok)

    split = build_graph([("A", "B", 3), ("C", "D", 2)])
    distance, previous = dijkstra(split, "A")
    check("Unreachable location gives infinity", distance["C"] == INFINITY)
    check("Unreachable location gives empty path", get_path(previous, "A", "C") == [])

    parcels, graph, capacity, depot = load_dataset("small")
    distance, previous = dijkstra(graph, depot)
    check("Small dataset: Depot to Uttam Nagar = 13 km", distance["Uttam Nagar"] == 13)
    check("Small dataset: path is Depot, Janakpuri, Uttam Nagar",
          get_path(previous, depot, "Uttam Nagar") == ["Depot", "Janakpuri", "Uttam Nagar"])
    check("Small dataset: Depot to Najafgarh = 22 km", distance["Najafgarh"] == 22)

    parcels, graph, capacity, depot = load_dataset("large")
    reference = floyd_warshall(graph)
    distance, previous = dijkstra(graph, depot)
    check("Large dataset: Dijkstra equals Floyd-Warshall from Depot",
          all(distance[p] == reference[depot][p] for p in graph))


def test_tsp():
    print()
    print("--- Nearest Neighbor TSP tests ---")
    places = ["D", "A", "B", "C"]
    matrix = {
        "D": {"D": 0, "A": 2, "B": 9, "C": 10},
        "A": {"D": 2, "A": 0, "B": 3, "C": 8},
        "B": {"D": 9, "A": 3, "B": 0, "C": 4},
        "C": {"D": 10, "A": 8, "B": 4, "C": 0},
    }
    route, total = nearest_neighbor("D", places, matrix)
    check("Hand-checked route D, A, B, C, D", route == ["D", "A", "B", "C", "D"])
    check("Hand-checked distance 2 + 3 + 4 + 10 = 19", total == 19)

    route, total = nearest_neighbor("D", ["D"], matrix)
    check("No places to visit gives route D, D with distance 0", route == ["D", "D"] and total == 0)

    route, total = nearest_neighbor("D", ["A"], matrix)
    check("One place gives a round trip (2 x 2 = 4)", route == ["D", "A", "D"] and total == 4)

    route, total = nearest_neighbor("D", ["A", "A", "B"], matrix)
    check("Duplicate places are visited once", route.count("A") == 1)

    random.seed(4)
    never_better = True
    total_matches = True
    for _ in range(20):
        count = random.randint(2, 6)
        g = random_graph(10)
        chosen = random.sample(list(g.keys()), count + 1)
        start = chosen[0]
        stops = chosen[1:]
        m = build_distance_matrix(g, chosen)
        route, total = nearest_neighbor(start, stops, m)
        best = INFINITY
        for order in permutations(stops):
            sequence = [start] + list(order) + [start]
            length = sum(m[sequence[i]][sequence[i + 1]] for i in range(len(sequence) - 1))
            if length < best:
                best = length
        if total < best:
            never_better = False
        if total != sum(m[route[i]][route[i + 1]] for i in range(len(route) - 1)):
            total_matches = False
    check("Route distance equals the sum of its legs (20 random cases)", total_matches)
    check("Nearest Neighbor is never shorter than the brute force optimum", never_better)


def test_integration():
    print()
    print("--- Integration tests (full pipeline) ---")
    for name in ["small", "large"]:
        parcels, graph, capacity, depot = load_dataset(name)
        check_data(parcels, graph, depot, capacity)
        sorted_parcels = merge_sort(parcels)
        best_value, selected, table = knapsack(sorted_parcels, capacity)
        destinations = []
        for p in selected:
            if p["destination"] != depot and p["destination"] not in destinations:
                destinations.append(p["destination"])
        matrix = build_distance_matrix(graph, [depot] + destinations)
        route, total = nearest_neighbor(depot, destinations, matrix)
        legs = expand_route(graph, route)
        leg_total = sum(leg[2] for leg in legs)
        road_total = sum(path_length(graph, leg[3]) for leg in legs)
        check(name + ": route starts and ends at the depot", route[0] == depot and route[-1] == depot)
        check(name + ": every destination of selected parcels is visited once",
              sorted(route[1:-1]) == sorted(destinations))
        check(name + ": total " + str(total) + " km = sum of legs = real road distance",
              total == leg_total == road_total)
        check(name + ": weight " + str(sum(p["weight"] for p in selected)) + " <= capacity " + str(capacity),
              sum(p["weight"] for p in selected) <= capacity)

    parcels, graph, capacity, depot = load_dataset("small")
    bad_parcels = [{"parcel_id": "Z1", "destination": "Mars", "weight": 5, "priority": 1, "deadline": 1, "value": 1}]
    try:
        check_data(bad_parcels, graph, depot, capacity)
        check("Unknown destination is rejected", False)
    except ValueError:
        check("Unknown destination is rejected", True)

    bad_parcels = [{"parcel_id": "Z2", "destination": "Palam", "weight": 0, "priority": 1, "deadline": 1, "value": 1}]
    try:
        check_data(bad_parcels, graph, depot, capacity)
        check("Zero weight is rejected", False)
    except ValueError:
        check("Zero weight is rejected", True)


test_sorting()
test_knapsack()
test_dijkstra()
test_tsp()
test_integration()

print()
print("Total tests:", passed + failed, "| Passed:", passed, "| Failed:", failed)
