from graph import dijkstra, get_path


def build_distance_matrix(graph, places):
    matrix = {}
    for place in places:
        distance, previous = dijkstra(graph, place)
        matrix[place] = {}
        for other in places:
            matrix[place][other] = distance[other]
    return matrix


def nearest_neighbor(start, places, matrix):
    unvisited = []
    for place in places:
        if place != start and place not in unvisited:
            unvisited.append(place)

    route = [start]
    total_distance = 0
    current = start

    while unvisited:
        nearest = unvisited[0]
        for place in unvisited:
            if matrix[current][place] < matrix[current][nearest]:
                nearest = place
        total_distance += matrix[current][nearest]
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    total_distance += matrix[current][start]
    route.append(start)
    return route, total_distance


def expand_route(graph, route):
    legs = []
    for i in range(len(route) - 1):
        distance, previous = dijkstra(graph, route[i])
        path = get_path(previous, route[i], route[i + 1])
        legs.append((route[i], route[i + 1], distance[route[i + 1]], path))
    return legs
