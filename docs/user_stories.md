# VendMate - User Stories

B215 Software Testing. Three types of user: Customer (no account),
Registered customer (has an account), and Admin (manages the machines).

---

**US1 - See what a machine has**
I want to see the slots, prices and stock before I buy.
- A slot with 0 stock shows "out of stock".
- The Buy button is off for a slot with 0 stock.

**US2 - Put coins in**
Coins go in one at a time and the balance goes up by that much. Valid
coins are 1, 5, 10, 25, 50 or 100 cents - anything else gets rejected
and the balance stays the same.

**US3 - Buy something.** Once I have enough money and the item is in
stock, buying it should drop the stock by 1 and show me the product
name plus my change.

**US4 - See how much more I need**

If I do not have enough money yet, I do not just want "insufficient
funds" - I want the exact number, so I know whether to add another coin
or give up and cancel.

- Balance under the price -> shows exact shortfall in cents.
- Stock and balance do not move.

**US5 - Cancel and get money back**
Cancelling resets my balance to 0 and tells me exactly how much came
back.

**US6 - Never get wrong change**

This one matters more than most of the others. If the machine cannot
make exact change for a purchase, it has to refuse the sale and say so
- it should never just hand back the wrong amount. Nothing changes when
this happens, not the stock and not the coin float.

**US7 - Make an account**
Want: an account so the app remembers my purchases.
Rule: free username + password of 4+ characters creates it. A taken
username or a short password gets rejected instead, no account made.

**US8 - See my past purchases**
As a registered customer, I want a list of what I have bought before -
date, machine, product, price, and change - so I can check my history.

---

Admin stories (US9-US11) are all about keeping a machine stocked and
working:

**US9 - Add more stock.** A non-negative amount increases a slot's
stock by that much; a negative amount gets rejected.

**US10 - Change a price.** A new price has to be more than 0, or it
gets rejected and the old price stays.

**US11 - Add coins to the float.** The coin type has to be one of the
valid denominations (1/5/10/25/50/100), or it gets rejected.

---

**US12 - See revenue per machine**
Admin wants a report showing total money made per machine, so they can
tell which one is actually worth restocking.

**US13 - Only admins can use admin pages**
Anyone who is not logged in as admin - whether that's an anonymous
visitor or a regular customer account - should get redirected away from
any `/admin/...` page with a message, and nothing on the backend should
change because of the attempt.
