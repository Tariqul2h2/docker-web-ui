from flask import Blueprint, render_template, redirect, url_for, session
from auth import login_handler, logout_handler

web = Blueprint('web', __name__)

@web.route("/")
def root():
    return redirect(url_for("web.dashboard"))

@web.route("/dashboard")
def dashboard():
    if "token" not in session:
        return redirect(url_for("web.login_page"))
    return render_template("dashboard.html", role=session.get("role"))

@web.route("/login", methods=["GET","POST"])
def login_page():
    return login_handler()

@web.route("/logout")
def logout():
    return logout_handler()
