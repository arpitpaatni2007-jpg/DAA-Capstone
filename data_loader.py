import csv
import json


def load_parcels(path):
    parcels = []
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            parcel = {
                "parcel_id": row["parcel_id"],
                "destination": row["destination"],
                "weight": int(row["weight"]),
                "priority": int(row["priority"]),
                "deadline": int(row["deadline"]),
                "value": int(row["value"]),
            }
            parcels.append(parcel)
    return parcels


def load_roads(path):
    roads = []
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            roads.append((row["location_a"], row["location_b"], int(row["distance"])))
    return roads


def load_vehicle(path):
    with open(path) as file:
        vehicle = json.load(file)
    return vehicle


def check_data(parcels, graph, depot, capacity):
    if depot not in graph:
        raise ValueError("Depot is not present in the road network")
    if capacity < 0:
        raise ValueError("Vehicle capacity cannot be negative")
    for parcel in parcels:
        if parcel["destination"] not in graph:
            raise ValueError("Destination of " + parcel["parcel_id"] + " is not in the road network")
        if parcel["weight"] <= 0:
            raise ValueError("Weight of " + parcel["parcel_id"] + " must be positive")
