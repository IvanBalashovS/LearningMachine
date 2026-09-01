import sys

def main():
    try:
        with open('/home/ivanbalashov/LearningMachine/lastTask/data.txt', 'r') as f:
            lines = f.read().split()
    except FileNotFoundError:
        return

    if not lines:
        print(0)
        return

    orders = [int(x) for x in lines]
    road_length_km = orders[0]
    orders.pop(0)

    points_count = road_length_km

    half = points_count // 2

    total_cost = 0
    for i in range(points_count):
        distance = i if i <= half else points_count - i
        total_cost += orders[i] * distance

    sum_near = sum(orders[k] for k in range(1, half + 1))
    sum_far = sum(orders[(points_count - k) % points_count] for k in range(1, half))

    best_cost = total_cost

    for pos in range(points_count - 1):
        change = orders[pos] + sum_far - sum_near
        total_cost += change

        if total_cost < best_cost:
            best_cost = total_cost

        to_remove = (pos - half + 1) % points_count
        sum_far += orders[pos] - orders[to_remove]

        to_remove_near = (pos + 1) % points_count
        to_add_near = (pos + half + 1) % points_count
        sum_near += orders[to_add_near] - orders[to_remove_near]

    print(best_cost * 3)

if __name__ == '__main__':
    main()