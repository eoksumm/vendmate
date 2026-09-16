# VendMate - Test Plan

Module B215 Software Testing.

## 1. Goals

- Every acceptance criterion in `docs/user_stories.md` (US1-US13) has at
  least one test. See `docs/test_cases.md` for the mapping.
- `Machine` works correctly at edge cases: exact price, one cent short,
  zero stock, empty coin float, a machine that cannot give change.
- Flask routes turn domain errors into correct HTTP responses, and admin
  pages are actually blocked for non-admins.
- `pytest` catches regressions automatically, with a coverage number
  behind it (`docs/coverage_report.md`).

## 2. Scope

In scope: `vendmate.domain` (Slot, Machine, make_change, exceptions),
`vendmate.repository` (users, machines, purchase log), and all Flask
routes in `vendmate.app`.

Out of scope: browser-level UI testing (no Selenium/Playwright), load
testing, and persistence across restarts (the repository is in-memory
only).

## 3. Test levels

- **Unit:** `tests/test_change.py` and `tests/test_slot.py` test one
  function or class at a time. No Flask, no Machine, no I/O.
- **Integration:** `tests/test_machine.py` tests `Machine` together with
  `make_change` and `Slot`. `tests/test_repository.py` tests user and
  machine access plus password hashing together.
- **System:** `tests/test_routes.py` uses Flask's test client to go
  through the whole stack: request, routing, session, template, domain
  and repository calls, and back out as HTML.

## 4. Test techniques

**Equivalence Partitioning** - test one value from each valid/invalid
group instead of every possible value. Purchase outcomes are a good
example: enough money, not enough, out of stock, unknown slot code -
four groups, one test each.

**Boundary Value Analysis** - test right at a limit and one step on
each side. Used this on exact price vs. one cent short, 0 stock, and a
coin float with just enough coins vs. one short.

For a purchase being basically a small state machine (idle, accepting
coins, dispense or refuse, back to idle), we also did some **State
Transition Testing** directly on the transitions: insert then buy
works, insert then cancel resets everything, and a failed buy has to
leave the state unchanged so a retry still works.

## 5. Tools

| Tool | Purpose |
|---|---|
| `pytest` | test runner |
| `pytest-cov` | coverage measurement |
| Flask's `app.test_client()` | route and system tests, no real server |
| `flake8` | static analysis |

## 6. Entry criteria

- The feature has a user story and acceptance criteria written down.
- The code imports and runs without errors.

## 7. Exit criteria

- All tests in `tests/` pass.
- Every acceptance criterion (US1-US13) is covered by at least one test.
- `flake8` is clean (see `docs/static_analysis.md`).
- Statement coverage is 90%+ (currently 98%, with 100% on
  `vendmate.domain`).
- Every defect in `docs/defect_log.md` is fixed or written up as a known
  limitation.
