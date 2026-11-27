import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import threading
import sheets
import helpers
import layout

load_dotenv()

save_lock = threading.Lock()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

# simple login page
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        user = helpers.find_user(email, sheets.getRows())

        # checks if user exists, and has paid
        if user is None:
            error = "We couldn't find that email address."
        else:
            session["email"] = user["email"]
            return redirect(url_for("seats"))

    return render_template("login.html", error=error)


@app.route("/seats")
def seats():
    if "email" not in session:
        return redirect(url_for("login"))

    user = helpers.find_user(session['email'], sheets.getRows())
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    rows = sheets.getRows()
    taken = sorted(helpers.taken_by_others(user["email"], rows))

    return render_template(
        "seats.html",
        user=user,
        taken=taken,
        tables=layout.get_tables(),
        features=layout.FEATURES,
        floor_w=layout.FLOOR_WIDTH,
        floor_h=layout.FLOOR_HEIGHT,
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/api/seats", methods=["POST"])
def save_seats():
    if "email" not in session:
        return jsonify(error="Please log in again."), 401

    data = request.get_json(silent=True) or {}
    chosen = data.get("seats", [])

    if (not isinstance(chosen, list)
            or not all(isinstance(s, str) for s in chosen)
            or len(chosen) != len(set(chosen))):
        return jsonify(error="Invalid seat selection."), 400

    if not set(chosen) <= layout.valid_seat_ids():
        return jsonify(error="One of those seats doesn't exist."), 400

    # Only one save at a time, so two people can't both claim a seat
    with save_lock:
        rows = sheets.getRows(fresh=True)  # always fresh when saving
        user = helpers.find_user(session["email"], rows)

        if user is None:
            session.clear()
            return jsonify(error="Your payment isn't recorded."), 403

        if len(chosen) > user["tickets"]:
            return jsonify(error="You've selected more seats than tickets."), 400

        taken = helpers.taken_by_others(user["email"], rows)
        if set(chosen) & taken:
            return jsonify(
                error="Sorry, one of those seats was just taken. Please choose another.",
                taken=sorted(taken),
            ), 409

        sheets.saveSeats(user["row"], chosen)

    return jsonify(ok=True)

@app.route("/api/taken")
def api_taken():
    if "email" not in session:
        return jsonify(error="Please log in again."), 401

    rows = sheets.getRows()
    user = helpers.find_user(session["email"], rows)
    if user is None:
        session.clear()
        return jsonify(error="Your payment isn't recorded."), 403

    return jsonify(taken=sorted(helpers.taken_by_others(user["email"], rows)))

if __name__ == "__main__":
    app.run(debug=True)
