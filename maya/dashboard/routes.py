from flask import render_template

from maya import app, config


@app.route("/")
def home():
    return render_template("dashboard/home.html",
                           title=config.get("APP_NAME", ''), app_name=config.get("APP_NAME", ''))
