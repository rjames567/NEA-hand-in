def binary_search(arr, target, comparison_func=None):
    if not len(arr):
        return None

    if comparison_func is None:
        comparison_func = lambda x: x
    # geeksforgeeks.org/python-program-for-binary-search/
    top = len(arr) - 1
    bottom = 0

    while bottom <= top:
        mid = (top + bottom) // 2
        if comparison_func(arr[mid]) > target:
            bottom = mid + 1
        elif comparison_func(arr[mid]) < target:
            top = mid - 1
        else:
            return mid

    return None

def linear_search(arr, target, comparison_func=None, first=True):
    if not len(arr):
        return None

    if comparison_func is None:
        num = arr.count(target)
        if num:
            if first:
                for i, k in enumerate(arr):
                    if k == target:
                        return i
            else:
                found = 0
                for i, k in enumerate(arr):
                    if k == target:
                        found += 1
                        if found == num:
                            return i
    else:
        if first:
            for i, k in enumerate(arr):
                if comparison_func(k) == target:
                    return i
        else:
            last = None
            for i, k in enumerate(arr):
                if comparison_func(k) == target:
                    last = i
            return last
    return None
