import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
import sheets
import helpers

load_dotenv()

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
        elif not user["paid"]:
            error = "Your payment hasn't been recorded yet. Please contact the organisers."
        else:
            session["email"] = user["email"]
            return redirect(url_for("seats"))

    return render_template("login.html", error=error)


@app.route("/seats")
def seats():
    if "email" not in session:
        return redirect(url_for("login"))

    user = helpers.find_user(session['email'], sheets.getRows())
    if user is None or not user["paid"]:
        session.clear()
        return redirect(url_for("login"))

    return render_template("seats.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
