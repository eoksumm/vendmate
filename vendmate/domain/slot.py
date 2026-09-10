"""One product slot inside a vending machine (e.g. "A1" -> Cola, 150 cents, qty 8)."""

from dataclasses import dataclass


@dataclass
class Slot:
    code: str
    name: str
    price_cents: int
    quantity: int

    def __post_init__(self) -> None:
        if not self.code:
            raise ValueError("slot code cannot be empty")
        if self.price_cents <= 0:
            raise ValueError("price must be positive")
        if self.quantity < 0:
            raise ValueError("quantity cannot be negative")
