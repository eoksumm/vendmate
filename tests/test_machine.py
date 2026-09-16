import pytest

from vendmate.domain import (
    ExactChangeOnlyError,
    InsufficientFundsError,
    InvalidDenominationError,
    Machine,
    OutOfStockError,
    Slot,
    UnknownSlotError,
)


@pytest.fixture
def machine():
    m = Machine(machine_id="M1", location="Library lobby")
    m.add_slot(Slot("A1", "Cola", price_cents=150, quantity=2))
    m.add_slot(Slot("A2", "Chips", price_cents=100, quantity=0))
    for denom, count in {100: 5, 50: 5, 25: 10, 10: 10, 5: 10, 1: 20}.items():
        m.load_coins(denom, count)
    return m


def test_inserting_a_coin_increases_balance(machine):
    assert machine.insert_coin(100) == 100
    assert machine.insert_coin(50) == 150


def test_inserting_an_invalid_denomination_is_rejected(machine):
    with pytest.raises(InvalidDenominationError):
        machine.insert_coin(2)


def test_buying_with_exact_change_needs_no_change_back(machine):
    machine.insert_coin(100)
    machine.insert_coin(50)
    purchase = machine.buy("A1")
    assert purchase.change_cents == 0
    assert purchase.change_coins == {}
    assert purchase.product_name == "Cola"


def test_buying_reduces_stock_by_one(machine):
    machine.insert_coin(100)
    machine.insert_coin(50)
    machine.buy("A1")
    assert machine.slots["A1"].quantity == 1


def test_buying_with_too_little_money_raises_insufficient_funds(machine):
    machine.insert_coin(100)
    with pytest.raises(InsufficientFundsError) as exc:
        machine.buy("A1")
    assert exc.value.shortfall_cents == 50


def test_insufficient_funds_leaves_stock_and_balance_untouched(machine):
    machine.insert_coin(100)
    with pytest.raises(InsufficientFundsError):
        machine.buy("A1")
    assert machine.slots["A1"].quantity == 2
    assert machine.balance_cents == 100


def test_buying_one_cent_short_of_the_price_still_fails(machine):
    # Boundary: 149 cents for a 150-cent item.
    for denom in (100, 25, 10, 10, 1, 1, 1, 1):
        machine.insert_coin(denom)
    assert machine.balance_cents == 149
    with pytest.raises(InsufficientFundsError):
        machine.buy("A1")


def test_buying_out_of_stock_slot_raises(machine):
    machine.insert_coin(100)
    with pytest.raises(OutOfStockError):
        machine.buy("A2")


def test_buying_unknown_slot_raises(machine):
    machine.insert_coin(100)
    with pytest.raises(UnknownSlotError):
        machine.buy("Z9")


def test_change_is_correct_for_overpayment(machine):
    machine.insert_coin(100)
    machine.insert_coin(100)  # 200 cents for a 150-cent item -> 50 change
    purchase = machine.buy("A1")
    assert purchase.change_cents == 50
    assert sum(d * c for d, c in purchase.change_coins.items()) == 50


def test_cancel_refunds_exactly_the_coins_inserted(machine):
    machine.insert_coin(100)
    machine.insert_coin(25)
    refunded = machine.cancel()
    assert sorted(refunded) == [25, 100]
    assert machine.balance_cents == 0


def test_cancel_then_buy_requires_inserting_money_again(machine):
    machine.insert_coin(100)
    machine.cancel()
    with pytest.raises(InsufficientFundsError):
        machine.buy("A1")


def test_exact_change_only_mode_blocks_purchase_when_float_cannot_pay_out(machine):
    empty = Machine(machine_id="M2", location="Break room", exact_change_only=True)
    empty.add_slot(Slot("A1", "Cola", price_cents=150, quantity=5))
    # no coins loaded, so overpayment can't be refunded
    empty.insert_coin(100)
    empty.insert_coin(100)
    with pytest.raises(ExactChangeOnlyError):
        empty.buy("A1")
    # A failed change calculation must not have touched stock or the float.
    assert empty.slots["A1"].quantity == 5


def test_a_coin_just_inserted_cannot_be_used_as_its_own_change(machine):
    # The float starts empty; the customer pays with a single 200-cent
    # combination for a 150-cent item. Even though the two coins just
    # inserted would technically add up to enough to make 50 cents change,
    # the machine must not "reuse" money from the same transaction.
    bare = Machine(machine_id="M3", location="Gym")
    bare.add_slot(Slot("A1", "Cola", price_cents=150, quantity=1))
    bare.insert_coin(100)
    bare.insert_coin(100)
    with pytest.raises(ExactChangeOnlyError):
        bare.buy("A1")


def test_restock_increases_quantity(machine):
    machine.restock("A2", 5)
    assert machine.slots["A2"].quantity == 5


def test_restock_rejects_negative_quantity(machine):
    with pytest.raises(ValueError):
        machine.restock("A2", -1)


def test_set_price_updates_price(machine):
    machine.set_price("A1", 175)
    assert machine.slots["A1"].price_cents == 175


def test_set_price_rejects_zero_or_negative(machine):
    with pytest.raises(ValueError):
        machine.set_price("A1", 0)


def test_add_slot_rejects_duplicate_code(machine):
    with pytest.raises(ValueError):
        machine.add_slot(Slot("A1", "Water", price_cents=100, quantity=1))


def test_load_coins_rejects_negative_count(machine):
    with pytest.raises(ValueError):
        machine.load_coins(25, -1)
