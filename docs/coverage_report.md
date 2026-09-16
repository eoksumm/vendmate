# VendMate - Test Coverage Report

```bash
pytest --cov=vendmate --cov-branch --cov-report=term-missing --cov-report=html
```

66 tests, 0 failed.

| Module | Statements | Branches | Coverage |
|---|---|---|---|
| `vendmate/__init__.py` | 1 | 0 | 100% |
| `vendmate/app.py` | 163 | 14 | 95% |
| `vendmate/domain/__init__.py` | 5 | 0 | 100% |
| `vendmate/domain/change.py` | 27 | 16 | 100% |
| `vendmate/domain/exceptions.py` | 18 | 0 | 100% |
| `vendmate/domain/machine.py` | 74 | 20 | 100% |
| `vendmate/domain/slot.py` | 14 | 6 | 100% |
| `vendmate/repository.py` | 68 | 12 | 100% |
| **Total** | **370** | **68** | **98%** |

**Function coverage: 50/51 (98%).** Counted every `def` in
`vendmate.domain`, `vendmate.repository` and `vendmate.app`. Only
`main()` is not covered, since it just starts a real dev server.

## Not covered

7 statements, all startup code:

- `app.py:37-41` - the `seed()` branch in `create_app()`. Only used
  when no repository is passed in. Tests always pass their own, so this
  never runs.
- `app.py:213, 217` - `main()` and the `if __name__` guard. Cannot call
  this from a test without it starting a live server.

## Reflection

`vendmate.domain` and `vendmate.repository` are both at 100%. This is
the most important part, the business rules.

Not tested: the UI in a real browser (no Selenium/Playwright), and
concurrency (two people buying from the same machine at the same time).
