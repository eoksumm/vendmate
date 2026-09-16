import pytest

from vendmate.domain import make_change

FULL_FLOAT = {100: 5, 50: 5, 25: 10, 10: 10, 5: 10, 1: 20}


def test_zero_amount_needs_no_coins():
    assert make_change(0, FULL_FLOAT) == {}


def test_negative_amount_is_rejected():
    with pytest.raises(ValueError):
        make_change(-1, FULL_FLOAT)


def test_exact_single_denomination_match():
    assert make_change(100, FULL_FLOAT) == {100: 1}


def test_uses_fewest_coins_possible():
    # 30 cents: a quarter + a nickel (2 coins) beats 3 dimes or 30 pennies.
    result = make_change(30, FULL_FLOAT)
    assert sum(result.values()) == 2
    assert result == {25: 1, 5: 1}


def test_one_cent_boundary_below_a_round_denomination():
    # 24 cents can't use a quarter, boundary just under 25
    result = make_change(24, FULL_FLOAT)
    assert result == {10: 2, 1: 4}


def test_returns_none_when_float_is_empty():
    assert make_change(50, {}) is None


def test_returns_none_when_amount_unreachable_with_available_denominations():
    # Only nickels and dimes available: 3 cents can never be made.
    assert make_change(3, {10: 5, 5: 5}) is None


def test_respects_limited_coin_counts():
    # only one quarter available, 50 cents needs two, so it falls back
    # to a different valid combination
    result = make_change(50, {25: 1, 10: 10, 5: 10, 1: 10})
    assert result is not None
    assert sum(d * c for d, c in result.items()) == 50


def test_returns_none_when_exact_amount_exceeds_available_stock():
    # Just one penny available, needs 2.
    assert make_change(2, {1: 1}) is None


def test_all_pennies_fallback_when_nothing_else_available():
    assert make_change(4, {1: 10}) == {1: 4}
