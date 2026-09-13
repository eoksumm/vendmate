"""Flask routes. The actual rules live in vendmate.domain and
vendmate.repository - this file just wires HTTP requests to them."""

import functools

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

from .domain import (
    ExactChangeOnlyError,
    InsufficientFundsError,
    InvalidDenominationError,
    OutOfStockError,
    UnknownSlotError,
)
from .repository import Repository, seed


def _parse_int(raw: str, field: str) -> int:
    """int(raw), but with a friendly error message instead of Python's
    default one if the value isn't a number."""
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise ValueError(f"'{field}' must be a whole number.") from None


def create_app(repo: Repository = None, secret_key: str = "dev-secret-change-me") -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = secret_key
    app.config["REPO"] = repo if repo is not None else Repository()

    if repo is None:
        seed(app.config["REPO"])
        try:
            app.config["REPO"].register_user("admin", "admin123")
        except ValueError:
            pass

    def get_repo() -> Repository:
        return app.config["REPO"]

    def get_machine_or_404(machine_id: str):
        try:
            return get_repo().get_machine(machine_id)
        except KeyError:
            abort(404, description=f"No machine '{machine_id}'.")

    def login_required(view):
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("username"):
                flash("Please log in first.")
                return redirect(url_for("login", next=request.path))
            return view(*args, **kwargs)

        return wrapped

    def admin_required(view):
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            if session.get("username") != "admin":
                flash("Admin access only.")
                return redirect(url_for("home"))
            return view(*args, **kwargs)

        return wrapped

    @app.route("/")
    def home():
        return render_template("home.html", machines=get_repo().list_machines())

    @app.route("/machines/<machine_id>")
    def machine_detail(machine_id):
        machine = get_machine_or_404(machine_id)
        return render_template("machine.html", machine=machine)

    @app.route("/machines/<machine_id>/insert", methods=["POST"])
    def insert_coin(machine_id):
        machine = get_machine_or_404(machine_id)
        try:
            machine.insert_coin(int(request.form["denomination"]))
        except (InvalidDenominationError, ValueError, KeyError):
            flash("Please choose a valid coin.")
        return redirect(url_for("machine_detail", machine_id=machine_id))

    @app.route("/machines/<machine_id>/buy", methods=["POST"])
    def buy(machine_id):
        repo = get_repo()
        machine = get_machine_or_404(machine_id)
        code = request.form.get("code", "")
        try:
            purchase = machine.buy(code)
            repo.record_purchase(machine_id, session.get("username"), purchase)
            flash(f"Dispensed {purchase.product_name}. Change: {purchase.change_cents} cent(s).")
        except UnknownSlotError:
            flash(f"No such slot '{code}'.")
        except OutOfStockError:
            flash("Sorry, that slot is out of stock.")
        except InsufficientFundsError as exc:
            flash(f"Insufficient funds - insert {exc.shortfall_cents} more cent(s).")
        except ExactChangeOnlyError:
            flash("Exact change only: this machine cannot make your change right now.")
        return redirect(url_for("machine_detail", machine_id=machine_id))

    @app.route("/machines/<machine_id>/cancel", methods=["POST"])
    def cancel(machine_id):
        machine = get_machine_or_404(machine_id)
        refunded = machine.cancel()
        flash(f"Refunded {sum(refunded)} cent(s)." if refunded else "Nothing to refund.")
        return redirect(url_for("machine_detail", machine_id=machine_id))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            try:
                get_repo().register_user(request.form["username"], request.form["password"])
                flash("Account created - please log in.")
                return redirect(url_for("login"))
            except ValueError as exc:
                flash(str(exc))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            user = get_repo().authenticate(request.form.get("username", ""), request.form.get("password", ""))
            if user:
                session["username"] = user.username
                return redirect(request.args.get("next") or url_for("home"))
            flash("Wrong username or password.")
        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    def logout():
        session.pop("username", None)
        return redirect(url_for("home"))

    @app.route("/account")
    @login_required
    def account():
        username = session["username"]
        history = get_repo().purchases_for_user(username)
        return render_template("account.html", username=username, history=history)

    @app.route("/admin/<machine_id>")
    @admin_required
    def admin_machine(machine_id):
        machine = get_machine_or_404(machine_id)
        return render_template("admin.html", machine=machine)

    @app.route("/admin/<machine_id>/restock", methods=["POST"])
    @admin_required
    def admin_restock(machine_id):
        machine = get_machine_or_404(machine_id)
        try:
            quantity = _parse_int(request.form["quantity"], "quantity")
            machine.restock(request.form["code"], quantity)
            flash("Restocked.")
        except (ValueError, UnknownSlotError, KeyError) as exc:
            flash(str(exc))
        return redirect(url_for("admin_machine", machine_id=machine_id))

    @app.route("/admin/<machine_id>/price", methods=["POST"])
    @admin_required
    def admin_price(machine_id):
        machine = get_machine_or_404(machine_id)
        try:
            price_cents = _parse_int(request.form["price_cents"], "price_cents")
            machine.set_price(request.form["code"], price_cents)
            flash("Price updated.")
        except (ValueError, UnknownSlotError, KeyError) as exc:
            flash(str(exc))
        return redirect(url_for("admin_machine", machine_id=machine_id))

    @app.route("/admin/<machine_id>/coins", methods=["POST"])
    @admin_required
    def admin_coins(machine_id):
        machine = get_machine_or_404(machine_id)
        try:
            denomination = _parse_int(request.form["denomination"], "denomination")
            count = _parse_int(request.form["count"], "count")
            machine.load_coins(denomination, count)
            flash("Coin float updated.")
        except (ValueError, InvalidDenominationError, KeyError) as exc:
            flash(str(exc))
        return redirect(url_for("admin_machine", machine_id=machine_id))

    @app.route("/admin/revenue")
    @admin_required
    def admin_revenue():
        repo = get_repo()
        return render_template("revenue.html", report=repo.revenue_report(), machines=repo.list_machines())

    @app.errorhandler(404)
    def not_found(error):
        message = getattr(error, "description", "Page not found.")
        return render_template("error.html", message=message), 404

    return app


def main() -> None:
    create_app().run(debug=True)


if __name__ == "__main__":
    main()
