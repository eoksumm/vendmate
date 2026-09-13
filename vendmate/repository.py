"""In-memory storage for machines, users, and the purchase log."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from werkzeug.security import check_password_hash, generate_password_hash

from .domain import Machine, Purchase, Slot


@dataclass
class User:
    username: str
    password_hash: str

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@dataclass
class PurchaseRecord:
    machine_id: str
    username: Optional[str]
    purchase: Purchase
    at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class Repository:
    def __init__(self) -> None:
        self.machines: Dict[str, Machine] = {}
        self.users: Dict[str, User] = {}
        self.purchases: List[PurchaseRecord] = []

    def add_machine(self, machine: Machine) -> None:
        self.machines[machine.machine_id] = machine

    def get_machine(self, machine_id: str) -> Machine:
        try:
            return self.machines[machine_id]
        except KeyError:
            raise KeyError(f"no machine '{machine_id}'") from None

    def list_machines(self) -> List[Machine]:
        return list(self.machines.values())

    def register_user(self, username: str, password: str) -> User:
        username = username.strip()
        if not username:
            raise ValueError("username cannot be empty")
        if len(password) < 4:
            raise ValueError("password must be at least 4 characters")
        if username in self.users:
            raise ValueError(f"username '{username}' is already taken")
        # scrypt (werkzeug's default) isn't available on every Python build,
        # so use pbkdf2 instead
        user = User(
            username=username,
            password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
        )
        self.users[username] = user
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.users.get(username)
        if user and user.check_password(password):
            return user
        return None

    def record_purchase(self, machine_id: str, username: Optional[str], purchase: Purchase) -> None:
        self.purchases.append(PurchaseRecord(machine_id=machine_id, username=username, purchase=purchase))

    def purchases_for_user(self, username: str) -> List[PurchaseRecord]:
        return [p for p in self.purchases if p.username == username]

    def revenue_report(self) -> Dict[str, int]:
        """Total revenue (in cents) per machine_id, across all recorded purchases."""
        report: Dict[str, int] = {}
        for record in self.purchases:
            report[record.machine_id] = report.get(record.machine_id, 0) + record.purchase.price_cents
        return report


def seed(repo: Repository) -> None:
    """Populates the repository with two demo machines, for a fresh install."""
    lobby = Machine(machine_id="M1", location="Library lobby")
    lobby.add_slot(Slot("A1", "Cola", price_cents=150, quantity=8))
    lobby.add_slot(Slot("A2", "Chips", price_cents=125, quantity=5))
    lobby.add_slot(Slot("A3", "Water", price_cents=100, quantity=10))
    for denom, count in {100: 10, 50: 10, 25: 20, 10: 20, 5: 20, 1: 40}.items():
        lobby.load_coins(denom, count)
    repo.add_machine(lobby)

    break_room = Machine(machine_id="M2", location="Staff break room", exact_change_only=True)
    break_room.add_slot(Slot("B1", "Coffee", price_cents=100, quantity=6))
    break_room.add_slot(Slot("B2", "Tea", price_cents=100, quantity=0))
    repo.add_machine(break_room)
