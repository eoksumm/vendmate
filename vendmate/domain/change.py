"""Works out change: can the machine make it, and with the fewest coins."""

from typing import Dict, Optional

VALID_DENOMINATIONS = (100, 50, 25, 10, 5, 1)


def make_change(amount: int, float_counts: Dict[int, int]) -> Optional[Dict[int, int]]:
    """Return {denomination: count} making up `amount` cents using no more
    coins of each denomination than float_counts allows, preferring the
    fewest total coins. Returns None if `amount` cannot be made exactly.

    Raises ValueError if `amount` is negative.
    """
    if amount < 0:
        raise ValueError("amount cannot be negative")
    if amount == 0:
        return {}

    # best[total] = the fewest-coin combination (as a {denom: count} dict)
    # that adds up to exactly `total`, considering denominations seen so far.
    best: Dict[int, Dict[int, int]] = {0: {}}

    for denom in sorted(float_counts, reverse=True):
        available = float_counts[denom]
        if available <= 0:
            continue
        updated = dict(best)
        for total, combo in best.items():
            coins_so_far = sum(combo.values())
            for k in range(1, available + 1):
                new_total = total + denom * k
                if new_total > amount:
                    break
                new_coin_count = coins_so_far + k
                current_best = updated.get(new_total)
                if current_best is None or sum(current_best.values()) > new_coin_count:
                    new_combo = dict(combo)
                    new_combo[denom] = new_combo.get(denom, 0) + k
                    updated[new_total] = new_combo
        best = updated

    return best.get(amount)
