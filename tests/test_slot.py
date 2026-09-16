import pytest

from vendmate.domain import Slot


def test_slot_rejects_empty_code():
    with pytest.raises(ValueError):
        Slot("", "Cola", price_cents=100, quantity=1)


def test_slot_rejects_non_positive_price():
    with pytest.raises(ValueError):
        Slot("A1", "Cola", price_cents=0, quantity=1)


def test_slot_rejects_negative_quantity():
    with pytest.raises(ValueError):
        Slot("A1", "Cola", price_cents=100, quantity=-1)


def test_slot_accepts_zero_quantity_boundary():
    s = Slot("A1", "Cola", price_cents=100, quantity=0)
    assert s.quantity == 0
