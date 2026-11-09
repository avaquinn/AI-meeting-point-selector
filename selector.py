from statistics import mean, pstdev

def main():
    times = [20, 21, 19, 20]
    print("MAD:", mean_absolute_deviation(times))
    print("Score:", score(times))


def score(times,
          total_weight=1.0,
          fairness_weight=0.7,
          worst_weight=0.3):

    total = sum(times)
    mad = mean_absolute_deviation(times)
    worst = max(times)

    n = len(times)

    return (
        total_weight * total
        + fairness_weight * n * mad
        + worst_weight * n * worst
    )

# Calculate mean absolute deviation from the mean.
def mean_absolute_deviation(times):
    if not times:
        raise ValueError("Travel times cannot be empty.")

    avg = mean(times)
    return mean(abs(t - avg) for t in times)

if __name__ == "__main__":
    main()
