def get_key(parcel):
    return (parcel["priority"], parcel["deadline"])


def merge(left, right):
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if get_key(left[i]) <= get_key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(parcels):
    if len(parcels) <= 1:
        return list(parcels)
    middle = len(parcels) // 2
    left = merge_sort(parcels[:middle])
    right = merge_sort(parcels[middle:])
    return merge(left, right)


def insertion_sort(parcels):
    items = list(parcels)
    for i in range(1, len(items)):
        current = items[i]
        j = i - 1
        while j >= 0 and get_key(items[j]) > get_key(current):
            items[j + 1] = items[j]
            j -= 1
        items[j + 1] = current
    return items
