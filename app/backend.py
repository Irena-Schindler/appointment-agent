"""In-memory calendar standing in for a real practice system."""
from datetime import date, time

OPENING = [time(h) for h in range(8, 17)]


class Calendar:
    def __init__(self) -> None:
        self.booked: set[tuple[date, time]] = set()
        self.callbacks: list[dict] = []

    def free_slots(self, day: date) -> list[str]:
        if day.weekday() >= 5:
            return []
        return [t.strftime("%H:%M") for t in OPENING if (day, t) not in self.booked]

    def book(self, day: date, start: time) -> bool:
        if start.strftime("%H:%M") not in self.free_slots(day):
            return False
        self.booked.add((day, start))
        return True

    def callback(self, entry: dict) -> None:
        self.callbacks.append(entry)
