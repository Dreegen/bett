from flask import Flask

app = Flask(__name__)

from app import routes

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
