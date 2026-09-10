"""Errors raised by the vending machine simulation."""


class VendingError(Exception):
    """Base class for every expected vending-machine failure."""


class UnknownSlotError(VendingError):
    def __init__(self, code: str):
        super().__init__(f"no slot with code '{code}'")
        self.code = code


class OutOfStockError(VendingError):
    def __init__(self, code: str):
        super().__init__(f"slot '{code}' is out of stock")
        self.code = code


class InsufficientFundsError(VendingError):
    def __init__(self, price_cents: int, inserted_cents: int):
        self.shortfall_cents = price_cents - inserted_cents
        super().__init__(f"needs {self.shortfall_cents} more cents")


class ExactChangeOnlyError(VendingError):
    """The machine's coin float cannot make the change owed for this purchase."""


class InvalidDenominationError(VendingError):
    def __init__(self, denomination: int):
        super().__init__(f"{denomination} is not a valid coin denomination")
        self.denomination = denomination
