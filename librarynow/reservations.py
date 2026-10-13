# librarynow/reservations.py
#
# NOTE: stand-in version written by our group because the lecturer's starter
# file was not available. It follows the LibraryNow rules in the Lab 8 text:
#   - students may reserve books
#   - at most three active reservations per student
#   - a reservation expires after 24 hours if not collected
#   - a borrowed book cannot be reserved

from dataclasses import dataclass, field
from datetime import datetime, timedelta

MAX_ACTIVE_RESERVATIONS = 3
RESERVATION_LIFETIME = timedelta(hours=24)

REASON_ACCEPTED = "Reservation accepted"
REASON_LIMIT = "Reservation limit reached"
REASON_BORROWED = "Book is currently borrowed"


@dataclass
class Reservation:
    book_id: str
    reserved_at: datetime


@dataclass
class Student:
    id: str
    reservations: list = field(default_factory=list)

    def active_reservations(self, now):
        # A reservation is active only while it is younger than 24 hours.
        return [r for r in self.reservations
                if now - r.reserved_at < RESERVATION_LIFETIME]


@dataclass
class Book:
    id: str
    borrowed: bool = False


class ReservationResult:
    def __init__(self, accepted, reason):
        self.accepted = accepted
        self.reason = reason


def may_reserve(student, book, now):
    """Decide whether `student` may reserve `book` at time `now`.

    `now` is passed in (instead of calling datetime.now()) so that tests can
    control the time without waiting.
    """
    if book.borrowed:
        return ReservationResult(False, REASON_BORROWED)
    if len(student.active_reservations(now)) >= MAX_ACTIVE_RESERVATIONS:
        return ReservationResult(False, REASON_LIMIT)
    return ReservationResult(True, REASON_ACCEPTED)
