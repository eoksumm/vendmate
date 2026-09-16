# VendMate - Static Analysis Summary

Tool: `flake8`, configured in `.flake8` with `max-line-length = 110`.

## First run

```
$ flake8 --max-line-length=110 vendmate tests
vendmate/app.py:187:111: E501 line too long (119 > 110 characters)
vendmate/domain/machine.py:7:1: F401 'typing.Optional' imported but unused
```

2 issues:

1. **app.py:187, line too long.** The `admin_revenue` view called
   `get_repo()` twice inside a `render_template(...)` call, which went
   past 110 characters. Fixed by storing it in a `repo` variable once
   and reusing it.

2. **machine.py:7, unused import.** `Optional` was imported for a
   method that was supposed to return `Optional[Slot]`, but it ended up
   raising an exception instead of returning `None`. The import was
   never used. Removed it.

## Second run

```
$ flake8 --max-line-length=110 vendmate tests
$ echo $?
0
```

Clean.
