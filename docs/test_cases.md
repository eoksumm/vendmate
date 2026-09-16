# VendMate - Test Cases

20 test cases (15 required). Each one is backed by a real `pytest` test.
All pass as of 2026-09-13. See `docs/coverage_report.md` for the full
test run.

---

### TC-01 - Exact payment, no change back (US3)
Technique: Boundary Value Analysis. Machine M1, slot A1 = Cola at 150
cents, stock 2. Insert 100 + 50 cents and buy A1. Expected: purchase
works, change is 0, stock drops to 1. That's what happens.
Severity: High. Pass.
`tests/test_machine.py::test_buying_with_exact_change_needs_no_change_back`

### TC-02 - One cent short still fails (US4)
Boundary Value Analysis, other side of the same limit. Slot A1 is 150
cents; insert 149 and try to buy.
- Expected: `InsufficientFundsError`, shortfall = 1, stock unchanged.
- Actual: matches.
- Severity: High. Pass.
`tests/test_machine.py::test_buying_one_cent_short_of_the_price_still_fails`

### TC-03 - A failed purchase should not change anything
Equivalence Partitioning. M1, slot A1, stock 2, price 150. Insert 100
cents only, try to buy, then check stock and balance afterward. Should
raise an error and leave stock at 2, balance at 100 - and it does.
Critical severity, since a rejected purchase silently eating coins would
be a serious bug. Pass.
`tests/test_machine.py::test_insufficient_funds_leaves_stock_and_balance_untouched`

### TC-04 - Buying an empty slot (US1/US3)
Boundary case: stock = 0. Slot A2 on M1 is empty; insert 100 cents and
try to buy it anyway.
- Expected: `OutOfStockError`
- Actual: `OutOfStockError`
- Severity: High. Pass.
`tests/test_machine.py::test_buying_out_of_stock_slot_raises`

### TC-05 - Typing a slot code that doesn't exist
The UI dropdown only ever shows real slot codes, but the domain layer
still needs to handle a bad one gracefully. Tried "Z9" on M1, expected
`UnknownSlotError` instead of a crash. Got it. Medium severity, passed.
`tests/test_machine.py::test_buying_unknown_slot_raises`

### TC-06 - Overpaying gives correct change back (US3)
Equivalence Partitioning. Slot A1 = 150 cents, insert 200, buy it.
Expected change = 50, and the coins handed back should sum to 50 -
confirmed. Critical, since wrong change math is about the worst bug a
vending machine could have. Pass.
`tests/test_machine.py::test_change_is_correct_for_overpayment`

### TC-07 - exact_change_only blocks a sale it can't pay change for (US6)
Boundary Value Analysis + State Transition. Machine set to
`exact_change_only=True`, empty float, price 150, insert 200 (owed 50
back). Since the float is empty it physically cannot give change, so
the whole sale must be refused rather than shorting the customer.
Expected `ExactChangeOnlyError`, stock unchanged - that's the result.
Critical severity. Pass.
`tests/test_machine.py::test_exact_change_only_mode_blocks_purchase_when_float_cannot_pay_out`

### TC-08 - Your own coin can't count as your own change (US6)
Related to TC-07 but a different bug. 200-150=50 looks fine on paper,
but that 200 is the customer's own money, not float money. Fresh
machine, empty float, price 150, insert 200, buy.
- Expected: `ExactChangeOnlyError` anyway
- Actual: matches
- Severity: High. Pass.
`tests/test_machine.py::test_a_coin_just_inserted_cannot_be_used_as_its_own_change`

### TC-09 - make_change should use the fewest coins possible
Not a user-facing story, more an internal correctness check on the
change algorithm. amount=30, float has plenty of every coin (100:5,
50:5, 25:10, 10:10, 5:10, 1:20). Expected `{25: 1, 5: 1}`, 2 coins -
matched. Medium severity, passed.
`tests/test_change.py::test_uses_fewest_coins_possible`

### TC-10 - make_change with a thin float (US6)
Boundary Value Analysis on coin counts, only 1 of the 25s left.
amount=50, float = {25: 1, 10: 10, 5: 10, 1: 10}.
- Expected: any valid combination that sums to 50
- Actual: got a valid combination
- Severity: High. Pass.
`tests/test_change.py::test_respects_limited_coin_counts`

### TC-11 - make_change returns None, not a crash, when it's impossible (US6)
amount=3 with float={10:5, 5:5} - no way to make 3 cents from 10s and
5s. Expected `None`, not an exception and not a wrong number. Got
`None`. Critical: a crash here would take down the whole purchase flow
instead of just failing that one sale cleanly. Pass.
`tests/test_change.py::test_returns_none_when_amount_unreachable_with_available_denominations`

### TC-12 - negative amount into make_change
Defensive test - this path probably isn't reachable from the UI, but
it's covered anyway. amount=-1 should raise `ValueError`, and does.
Low severity. Pass.
`tests/test_change.py::test_negative_amount_is_rejected`

### TC-13 - Cancelling refunds exactly what was put in (US5)
Insert 100 then 25 cents, cancel.
- Expected: refunded = [25, 100], balance back to 0
- Actual: matches
- Severity: High. Pass.
`tests/test_machine.py::test_cancel_refunds_exactly_the_coins_inserted`

### TC-14 - The full purchase flow through the actual website (US3)
System-level test using Flask's test client rather than the domain
layer directly - closer to what a real user does. POST insert 100, POST
insert 50, POST buy "A1", follow the redirects. Expected the final page
to say "Dispensed Cola" somewhere, which it does. Critical, since this
is the core flow of the whole app. Pass.
`tests/test_routes.py::test_full_purchase_flow_via_the_web_client`

### TC-15 - Hitting a machine ID that doesn't exist (US1)
GET `/machines/DOES-NOT-EXIST`.
- Expected: plain HTTP 404, not a 500 or a traceback
- Actual: 404
- Severity: Medium. Pass.
`tests/test_routes.py::test_unknown_machine_returns_404`

### TC-16 - A logged-in but non-admin user can't reach admin pages (US13)
Equivalence Partitioning across the three user types. GET `/admin/M1`
while logged in as a regular customer. Expected a redirect with "Admin
access only" - got exactly that. Critical severity, since this is a
real access-control check. Pass.
`tests/test_routes.py::test_admin_page_is_blocked_for_non_admin_users`

### TC-17 - Can't register the same username twice (US7)
Register "bob", then try again with "bob". Second attempt should fail
with something like "already taken" instead of silently overwriting the
first account. Got the right message. Medium severity, passed.
`tests/test_routes.py::test_registering_a_duplicate_username_is_rejected`

### TC-18 - Bad admin input shows a real message, not a traceback (DEF-3)
Regression test for DEF-3 (see `docs/defect_log.md`). Set quantity="abc"
in the admin restock form.
- Expected: a message like "must be a whole number"
- Actual: matches (and fails without the `_parse_int()` fix, which is
  how DEF-3 was actually found)
- Severity: Medium. Pass.
`tests/test_routes.py::test_admin_restock_with_non_numeric_quantity_shows_a_friendly_message`

### TC-19 - Revenue report matches what was actually sold (US12)
Make one purchase worth 150 cents on M1, then GET `/admin/revenue`.
Expected the report to show 1.50 for M1, calculated from the purchase
log rather than a hardcoded number - it does. High severity. Pass.
`tests/test_routes.py::test_admin_revenue_report_reflects_purchases`

### TC-20 - Password under 4 characters gets rejected (US7)
Boundary Value Analysis right at the limit, password="abc" (3 chars).
- Expected: `ValueError`, no account created
- Actual: matches
- Severity: Medium. Pass.
`tests/test_repository.py::test_register_user_rejects_short_password`

---

All 20 pass. 66 tests total in the full suite - see
`docs/coverage_report.md` for the complete run.
