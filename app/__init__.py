import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
import datetime
from peewee import (
    SqliteDatabase,
    MySQLDatabase,
    Model,
    CharField,
    TextField,
    DateTimeField,
)
from playhouse.shortcuts import model_to_dict

load_dotenv()
app = Flask(__name__)

if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase("file:memory?mode=memory&cache=shared", uri=True)
else:
    mydb = MySQLDatabase(
        os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=3306,
    )

print(mydb)


class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = mydb


mydb.connect()
mydb.create_tables([TimelinePost])


def check_errors(form: dict):
    errors = []
    if "name" not in form or len(form["name"].strip()) < 1:
        errors.append("Invalid name")
    if (
        "email" not in form
        or len(form["email"].strip()) < 1
        or "@" not in form["email"]
    ):
        errors.append("Invalid email")
    if "content" not in form or len(form["content"].strip()) < 1:
        errors.append("Invalid content")
    return errors


@app.route("/")
def index():
    return render_template("index.html", title="MLH Fellow", url=os.getenv("URL")), 200


@app.route("/timeline")
def timeline():
    return render_template("timeline.html", title="Timeline", url=os.getenv("URL")), 200


@app.route("/api/timeline_post", methods=["POST"])
def api_post_time_line_post():
    errors = check_errors(request.form)
    if errors:
        return {"errors": errors}, 400

    name = request.form["name"].strip()
    email = request.form["email"].strip()
    content = request.form["content"].strip()

    timeline_post = TimelinePost.create(name=name, email=email, content=content)
    return model_to_dict(timeline_post), 200


@app.route("/api/timeline_post", methods=["GET"])
def get_timeline_post():
    return {
        "timeline_posts": [
            model_to_dict(p)
            for p in TimelinePost.select().order_by(TimelinePost.created_at.desc())
        ]
    }, 200
