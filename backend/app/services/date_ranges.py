from datetime import date, timedelta


def ranges_overlap(start_a: date, end_a: date, start_b: date, end_b: date) -> bool:
    return start_a < end_b and start_b < end_a


def each_night(check_in: date, check_out: date) -> list[date]:
    nights: list[date] = []
    current = check_in
    while current < check_out:
        nights.append(current)
        current += timedelta(days=1)
    return nights
