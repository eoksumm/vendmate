"""The vending machine simulation logic. No Flask or database code here,
just plain Python, so it can be tested without running a server."""

from .change import make_change
from .exceptions import (
    ExactChangeOnlyError,
    InsufficientFundsError,
    InvalidDenominationError,
    OutOfStockError,
    UnknownSlotError,
    VendingError,
)
from .machine import Machine, Purchase
from .slot import Slot

__all__ = [
    "make_change",
    "ExactChangeOnlyError",
    "InsufficientFundsError",
    "InvalidDenominationError",
    "OutOfStockError",
    "UnknownSlotError",
    "VendingError",
    "Machine",
    "Purchase",
    "Slot",
]
