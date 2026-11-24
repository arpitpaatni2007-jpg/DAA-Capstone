def knapsack(parcels, capacity):
    n = len(parcels)
    table = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        weight = parcels[i - 1]["weight"]
        value = parcels[i - 1]["value"]
        for w in range(capacity + 1):
            table[i][w] = table[i - 1][w]
            if weight <= w:
                with_parcel = table[i - 1][w - weight] + value
                if with_parcel > table[i][w]:
                    table[i][w] = with_parcel

    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if table[i][w] != table[i - 1][w]:
            selected.append(parcels[i - 1])
            w -= parcels[i - 1]["weight"]
    selected.reverse()

    return table[n][capacity], selected, table
