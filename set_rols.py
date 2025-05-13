from flask import Flask
from extensions import mongo
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo.init_app(app)

with app.app_context():
    email_admin = "admin@example.com"  # ← canvia-ho pel correu del profe
    result = mongo.db.professors.update_one(
        {"email": email_admin},
        {"$set": {"rol": "admin"}}
    )
    if result.modified_count > 0:
        print("Professor promogut a administrador.")
    else:
        print("Cap professor actualitzat.")
