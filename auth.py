from flask import session, redirect, url_for, render_template, request
from flask_jwt_extended import create_access_token
from models import find_user
from passlib.hash import bcrypt

def login_handler():
    if request.method == "POST":
        user = find_user(request.form["username"])
        if user and bcrypt.verify(request.form["password"], user["password"]):
            token = create_access_token(identity=user["username"], additional_claims={"role": user["role"]})
            session["token"] = token
            session["role"] = user["role"]
            return redirect(url_for("web.dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

def logout_handler():
    session.clear()
    return redirect(url_for("login_page"))
