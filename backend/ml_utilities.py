# -----------------------------------------------------------------------------
# Similarity Measures
# -----------------------------------------------------------------------------
# https://www.kdnuggets.com/2020/11/most-popular-distance-metrics-knn.html
# https://milvus.io/docs/metric.md
import math


def jaccard_similarity(set_1, set_2):
    # set_1 and set_2 must be sets not lists.
    # Sets are faster for union+intersection etc, as they are unordered and cannot have duplicate values.
    union = set_1.union(set_2)
    intersection = set_1.intersection(set_2)
    return len(intersection) / len(union)

def cosine_similarity(arr1, arr2):
    return (sum(i * k for i, k in zip(arr1, arr2)) / (
                math.sqrt(sum(i ** 2 for i in arr1)) *
                math.sqrt(sum(i ** 2 for i in arr2))
            )
        )

# -----------------------------------------------------------------------------
# Error measures
# -----------------------------------------------------------------------------
def mean_squared_error(true, predicted):
    return sum((i - k)**2 for i, k in zip(true, predicted)) / len(true)
