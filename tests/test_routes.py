"""Route tests using Flask's test client, on a freshly seeded repository."""


def login(client, username="admin", password="admin123"):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


def test_home_page_lists_seeded_machines(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"M1" in resp.data
    assert b"Library lobby" in resp.data


def test_unknown_machine_returns_404(client):
    resp = client.get("/machines/DOES-NOT-EXIST")
    assert resp.status_code == 404


def test_full_purchase_flow_via_the_web_client(client):
    client.post("/machines/M1/insert", data={"denomination": "100"})
    client.post("/machines/M1/insert", data={"denomination": "50"})
    resp = client.post("/machines/M1/buy", data={"code": "A1"}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Dispensed Cola" in resp.data


def test_buying_without_enough_money_shows_a_message(client):
    client.post("/machines/M1/insert", data={"denomination": "10"})
    resp = client.post("/machines/M1/buy", data={"code": "A1"}, follow_redirects=True)
    assert b"Insufficient funds" in resp.data


def test_cancel_refunds_and_resets_balance(client):
    client.post("/machines/M1/insert", data={"denomination": "25"})
    resp = client.post("/machines/M1/cancel", data={}, follow_redirects=True)
    assert b"Refunded 25 cent" in resp.data


def test_buying_out_of_stock_slot_shows_a_message(client):
    client.post("/machines/M2/insert", data={"denomination": "100"})
    resp = client.post("/machines/M2/buy", data={"code": "B2"}, follow_redirects=True)
    assert b"out of stock" in resp.data


def test_register_page_renders_on_get(client):
    resp = client.get("/register")
    assert resp.status_code == 200
    assert b"Create an account" in resp.data


def test_register_then_login_then_logout(client):
    client.post("/register", data={"username": "alice", "password": "secretpw"})
    resp = login(client, "alice", "secretpw")
    assert b"Hi, alice" in resp.data
    resp = client.post("/logout", follow_redirects=True)
    assert b"Hi, alice" not in resp.data


def test_registering_a_duplicate_username_is_rejected(client):
    client.post("/register", data={"username": "bob", "password": "secretpw"})
    resp = client.post("/register", data={"username": "bob", "password": "other-pw"}, follow_redirects=True)
    assert b"already taken" in resp.data


def test_login_with_wrong_password_is_rejected(client):
    client.post("/register", data={"username": "carol", "password": "secretpw"})
    resp = client.post("/login", data={"username": "carol", "password": "wrong"}, follow_redirects=True)
    assert b"Wrong username or password" in resp.data


def test_account_page_requires_login(client):
    resp = client.get("/account", follow_redirects=True)
    assert b"Please log in first" in resp.data or b"Log in" in resp.data


def test_purchase_is_recorded_in_logged_in_users_history(client):
    client.post("/register", data={"username": "dave", "password": "secretpw"})
    login(client, "dave", "secretpw")
    client.post("/machines/M1/insert", data={"denomination": "100"})
    client.post("/machines/M1/insert", data={"denomination": "50"})
    client.post("/machines/M1/buy", data={"code": "A1"})
    resp = client.get("/account")
    assert b"Cola" in resp.data


def test_admin_page_is_blocked_for_non_admin_users(client):
    client.post("/register", data={"username": "eve", "password": "secretpw"})
    login(client, "eve", "secretpw")
    resp = client.get("/admin/M1", follow_redirects=True)
    assert b"Admin access only" in resp.data


def test_admin_can_restock_a_slot(client):
    login(client)
    resp = client.post("/admin/M2/restock", data={"code": "B2", "quantity": "3"}, follow_redirects=True)
    assert b"Restocked" in resp.data
    # the slot should now be buyable
    client.post("/machines/M2/insert", data={"denomination": "100"})
    resp = client.post("/machines/M2/buy", data={"code": "B2"}, follow_redirects=True)
    assert b"Dispensed Tea" in resp.data


def test_admin_can_update_a_price(client):
    login(client)
    resp = client.post("/admin/M1/price", data={"code": "A3", "price_cents": "120"}, follow_redirects=True)
    assert b"Price updated" in resp.data
    resp = client.get("/machines/M1")
    assert b"1.20" in resp.data


def test_inserting_an_invalid_coin_shows_a_message(client):
    resp = client.post("/machines/M1/insert", data={"denomination": "2"}, follow_redirects=True)
    assert b"Please choose a valid coin" in resp.data


def test_buying_an_unknown_slot_code_shows_a_message(client):
    client.post("/machines/M1/insert", data={"denomination": "100"})
    resp = client.post("/machines/M1/buy", data={"code": "Z9"}, follow_redirects=True)
    assert b"No such slot" in resp.data


def test_exact_change_only_machine_blocks_a_purchase_it_cannot_pay_change_for(client):
    # M2 is exact_change_only and starts with an empty coin float.
    client.post("/machines/M2/insert", data={"denomination": "100"})
    client.post("/machines/M2/insert", data={"denomination": "1"})
    resp = client.post("/machines/M2/buy", data={"code": "B1"}, follow_redirects=True)
    assert b"Exact change only" in resp.data


def test_admin_restock_with_invalid_quantity_shows_a_message(client):
    login(client)
    resp = client.post("/admin/M1/restock", data={"code": "A1", "quantity": "-1"}, follow_redirects=True)
    assert b"cannot be negative" in resp.data


def test_admin_restock_unknown_slot_shows_a_message(client):
    login(client)
    resp = client.post("/admin/M1/restock", data={"code": "Z9", "quantity": "1"}, follow_redirects=True)
    assert b"no slot" in resp.data


def test_admin_price_with_zero_is_rejected(client):
    login(client)
    resp = client.post("/admin/M1/price", data={"code": "A1", "price_cents": "0"}, follow_redirects=True)
    assert b"must be positive" in resp.data


def test_admin_restock_with_non_numeric_quantity_shows_a_friendly_message(client):
    login(client)
    resp = client.post("/admin/M1/restock", data={"code": "A1", "quantity": "abc"}, follow_redirects=True)
    assert b"must be a whole number" in resp.data
    assert b"invalid literal" not in resp.data


def test_admin_can_load_coins_into_the_float(client):
    login(client)
    resp = client.post("/admin/M1/coins", data={"denomination": "25", "count": "10"}, follow_redirects=True)
    assert b"Coin float updated" in resp.data


def test_admin_coins_with_invalid_denomination_shows_a_message(client):
    login(client)
    resp = client.post("/admin/M1/coins", data={"denomination": "2", "count": "5"}, follow_redirects=True)
    assert b"not a valid coin denomination" in resp.data


def test_admin_revenue_report_reflects_purchases(client):
    login(client)
    client.post("/machines/M1/insert", data={"denomination": "100"})
    client.post("/machines/M1/insert", data={"denomination": "50"})
    client.post("/machines/M1/buy", data={"code": "A1"})
    resp = client.get("/admin/revenue")
    assert b"1.50" in resp.data
