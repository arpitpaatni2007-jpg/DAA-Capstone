import heapq

INFINITY = float("inf")


def build_graph(roads):
    graph = {}
    for place_a, place_b, distance in roads:
        if place_a not in graph:
            graph[place_a] = {}
        if place_b not in graph:
            graph[place_b] = {}
        graph[place_a][place_b] = distance
        graph[place_b][place_a] = distance
    return graph


def dijkstra(graph, source):
    distance = {}
    previous = {}
    for place in graph:
        distance[place] = INFINITY
        previous[place] = None
    distance[source] = 0

    heap = [(0, source)]
    while heap:
        current_distance, place = heapq.heappop(heap)
        if current_distance > distance[place]:
            continue
        for neighbor, road_length in graph[place].items():
            new_distance = current_distance + road_length
            if new_distance < distance[neighbor]:
                distance[neighbor] = new_distance
                previous[neighbor] = place
                heapq.heappush(heap, (new_distance, neighbor))

    return distance, previous


def get_path(previous, source, target):
    path = []
    place = target
    while place is not None:
        path.append(place)
        place = previous[place]
    path.reverse()
    if path[0] != source:
        return []
    return path
