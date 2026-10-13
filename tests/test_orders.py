import pytest
from campusgo.orders import order_total, Order

def test_ten_percent_discount_at_subtotal_50000():
    # Arrange
    price, qty = 25000, 2

    # Act
    total = order_total(price, qty, has_promo=True)

    # Assert
    assert total == 45000


def test_total_is_67500_for_three_items_with_promo():
    total = order_total(25000, 3, has_promo=True)
    assert total == 67500


def test_error_message_mentions_qty():
    with pytest.raises(ValueError) as err:
        order_total(25000, 0)
    assert "qty" in str(err.value)


def test_new_order_has_no_notifications():
    order = Order(id="ORD-T001", owner="U-01", total=25000)
    assert len(order.tenant_notifications) == 0


def test_zero_qty_is_rejected():
    with pytest.raises(ValueError) as err:
        order_total(25000, 0)
    assert "qty" in str(err.value)


def test_negative_qty_is_rejected():
    with pytest.raises(ValueError) as err:
        order_total(25000, -1)
    assert "qty" in str(err.value)


@pytest.fixture
def processing_order():
    # Arrange: precondition (ORD-T003, owned by Student A, PROCESSING)
    order = Order(id="ORD-T003", owner="U-01", total=25000)
    order.status = "PROCESSING"
    yield order          # the test runs at this point
    order.delete()       # cleanup after the test


def test_cancelling_processing_order_is_rejected(processing_order):
    # Act
    result = processing_order.cancel(by="U-01")

    # Assert: three layers of the expected result
    assert result.rejected is True                       # screen layer
    assert processing_order.status == "PROCESSING"       # data layer
    assert processing_order.tenant_notifications == []   # side-effect layer


@pytest.mark.parametrize("price, qty, promo, expected", [
    (25000, 1, True, 25000),    # subtotal Rp25,000: below the threshold
    (25000, 2, True, 45000),    # subtotal Rp50,000: exactly at the threshold
    (25000, 3, True, 67500),    # subtotal Rp75,000: above the threshold
    (25000, 2, False, 50000),   # no promo: no discount applies
])
def test_discount_br_07(price, qty, promo, expected):
    assert order_total(price, qty, promo) == expected