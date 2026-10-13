# tests/test_reservations.py
# Lab 8 - LibraryNow challenge (unit tests with pytest)

from datetime import datetime, timedelta

import pytest

from librarynow.reservations import (
    REASON_ACCEPTED,
    REASON_BORROWED,
    REASON_LIMIT,
    Book,
    Reservation,
    Student,
    may_reserve,
)

# Step 1 - fixed point in time, so no test depends on the real clock
NOW = datetime(2026, 10, 13, 9, 0)


def make_student(count, reserved_at=NOW):
    """Helper: a student holding `count` reservations made at `reserved_at`."""
    return Student(
        id="S-01",
        reservations=[
            Reservation(book_id=f"B-{i}", reserved_at=reserved_at)
            for i in range(count)
        ],
    )


# Step 5 - fixture: a student holding three active reservations (with cleanup)
@pytest.fixture
def student_with_three_reservations():
    # Arrange: precondition
    student = make_student(3)
    yield student  # the test runs at this point
    student.reservations.clear()  # cleanup after the test


# Step 2 - positive test
def test_student_with_zero_reservations_can_reserve_available_book():
    # Arrange
    student = make_student(0)
    book = Book(id="B-10")

    # Act
    result = may_reserve(student, book, NOW)

    # Assert
    assert result.accepted is True
    assert result.reason == REASON_ACCEPTED


# Step 3 - negative test: three-reservation limit (uses the fixture)
def test_fourth_reservation_is_rejected_with_limit_reason(
    student_with_three_reservations,
):
    # Act
    result = may_reserve(student_with_three_reservations, Book(id="B-10"), NOW)

    # Assert: check the refusal AND the reason
    assert result.accepted is False
    assert result.reason == REASON_LIMIT


# Step 4 - negative test: book already borrowed
def test_borrowed_book_cannot_be_reserved():
    # Arrange
    student = make_student(0)
    book = Book(id="B-10", borrowed=True)

    # Act
    result = may_reserve(student, book, NOW)

    # Assert: check the refusal AND the reason
    assert result.accepted is False
    assert result.reason == REASON_BORROWED


# Step 6 - parameterised test: reservation counts 0, 2, 3 and 4
@pytest.mark.parametrize(
    "count, accepted",
    [
        (0, True),   # no reservations yet
        (2, True),   # one below the limit
        (3, False),  # exactly at the limit (boundary)
        (4, False),  # above the limit
    ],
)
def test_reservation_limit_boundary(count, accepted):
    result = may_reserve(make_student(count), Book(id="B-10"), NOW)

    assert result.accepted is accepted


# Step 7 - 24-hour expiry: inject `now`, no waiting in real time
def test_expired_reservations_no_longer_count_after_25_hours(
    student_with_three_reservations,
):
    # Arrange: all three reservations were made at NOW; 25 hours pass
    later = NOW + timedelta(hours=25)

    # Act
    result = may_reserve(student_with_three_reservations, Book(id="B-10"), later)

    # Assert: the old reservations have expired, so the new one is accepted
    assert result.accepted is True
    assert result.reason == REASON_ACCEPTED
    # Weakness: this only tests the time-difference calculation, not the real
    # scheduler that expires reservations in production.