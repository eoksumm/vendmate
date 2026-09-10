# VendMate

A vending machine simulator web app, made for module B215 (Software Testing).

You insert coins, pick a product, and get it back with the right change
(or an error if something's wrong: not enough money, out of stock, etc).
Admins can restock slots, change prices, top up the coin float, and see
how much each machine has made.

## Why a vending machine

A vending machine has a lot of edge cases (exact price, one cent short,
empty stock, not enough coins for change) which made it a good app to
practice testing techniques like Equivalence Partitioning and Boundary
Value Analysis on.

## Project structure

```
vendmate/
├── vendmate/
│   ├── domain/          Slot, Machine, make_change, exceptions (no Flask here)
│   ├── repository.py    in-memory users / machines / purchase log
│   ├── app.py           Flask routes
│   ├── templates/       HTML pages
│   └── static/          style.css
├── tests/                pytest suite
├── docs/
│   ├── user_stories.md       user stories + acceptance criteria
│   ├── test_plan.md          test plan
│   ├── test_cases.md         test cases
│   ├── defect_log.md         bugs found during testing
│   ├── static_analysis.md    flake8 results
│   └── coverage_report.md    test coverage
├── pyproject.toml
├── requirements.txt
└── .flake8
```

## Install & run

```bash
python3 -m pip install -e ".[test]"
python3 -m vendmate.app       # runs on http://127.0.0.1:5000
```

Demo admin login: username `admin`, password `admin123`. Two machines
are seeded: `M1` (Library lobby) and `M2` (Staff break room, exact change
only).

## Running the tests

```bash
pytest --cov=vendmate --cov-branch --cov-report=term-missing
```

66 tests, 98% coverage. See `docs/coverage_report.md` for details.

## Static analysis

```bash
flake8 --max-line-length=110 vendmate tests
```

## Known limitation

The data is only stored in memory, so restarting the app resets it back
to the demo data. We decided this was fine for this project given the
time we had.
