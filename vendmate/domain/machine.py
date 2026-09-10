"""The vending machine: insert coins, select a slot, get the product plus
change back (or a clear error)."""

from dataclasses import dataclass, field
from typing import Dict, List

from .change import VALID_DENOMINATIONS, make_change
from .exceptions import (
    ExactChangeOnlyError,
    InsufficientFundsError,
    InvalidDenominationError,
    OutOfStockError,
    UnknownSlotError,
)
from .slot import Slot


@dataclass
class Purchase:
    slot_code: str
    product_name: str
    price_cents: int
    change_cents: int
    change_coins: Dict[int, int]


@dataclass
class Machine:
    machine_id: str
    location: str
    slots: Dict[str, Slot] = field(default_factory=dict)
    coin_float: Dict[int, int] = field(
        default_factory=lambda: {d: 0 for d in VALID_DENOMINATIONS}
    )
    exact_change_only: bool = False
    inserted_coins: List[int] = field(default_factory=list)

    def add_slot(self, slot: Slot) -> None:
        if slot.code in self.slots:
            raise ValueError(f"slot '{slot.code}' already exists")
        self.slots[slot.code] = slot

    def restock(self, code: str, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("quantity to add cannot be negative")
        self._get_slot(code).quantity += quantity

    def set_price(self, code: str, price_cents: int) -> None:
        if price_cents <= 0:
            raise ValueError("price must be positive")
        self._get_slot(code).price_cents = price_cents

    def load_coins(self, denomination: int, count: int) -> None:
        self._check_denomination(denomination)
        if count < 0:
            raise ValueError("count cannot be negative")
        self.coin_float[denomination] = self.coin_float.get(denomination, 0) + count

    @property
    def balance_cents(self) -> int:
        return sum(self.inserted_coins)

    def insert_coin(self, denomination: int) -> int:
        self._check_denomination(denomination)
        self.inserted_coins.append(denomination)
        return self.balance_cents

    def cancel(self) -> List[int]:
        """Refund exactly the coins the customer put in, and reset the
        transaction. Returns the list of denominations refunded."""
        refunded, self.inserted_coins = self.inserted_coins, []
        return refunded

    def buy(self, code: str) -> Purchase:
        slot = self._get_slot(code)
        if slot.quantity <= 0:
            raise OutOfStockError(code)

        balance = self.balance_cents
        if balance < slot.price_cents:
            raise InsufficientFundsError(slot.price_cents, balance)

        change_owed = balance - slot.price_cents
        # use the float as it was before this purchase, so a coin the
        # customer just inserted can't be handed straight back as change
        change_coins = make_change(change_owed, self.coin_float) if change_owed else {}
        if change_coins is None:
            raise ExactChangeOnlyError(
                f"cannot make {change_owed} cents change with the current coin float"
            )

        slot.quantity -= 1
        for denomination in self.inserted_coins:
            self.coin_float[denomination] = self.coin_float.get(denomination, 0) + 1
        for denomination, count in change_coins.items():
            self.coin_float[denomination] -= count
        self.inserted_coins = []

        return Purchase(
            slot_code=code,
            product_name=slot.name,
            price_cents=slot.price_cents,
            change_cents=change_owed,
            change_coins=change_coins,
        )

    def _get_slot(self, code: str) -> Slot:
        try:
            return self.slots[code]
        except KeyError:
            raise UnknownSlotError(code) from None

    @staticmethod
    def _check_denomination(denomination: int) -> None:
        if denomination not in VALID_DENOMINATIONS:
            raise InvalidDenominationError(denomination)
