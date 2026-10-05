from statistics import mean, pstdev

def main():
    print("Foo");

def score(times,
          total_weight=1.0,
          fairness_weight=0.7,
          worst_weight=0.3):

    total = sum(times)
    std = pstdev(times)
    worst = max(times)

    n = len(times)

    return (
        total_weight * total
        + fairness_weight * n * std
        + worst_weight * n * worst
    )

if __name__ == "__main__":
    main()
