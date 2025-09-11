from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from models import init_db, add_user, find_user
from routes.web import web
from routes.api import api
import os

app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)

# Initialize DB and ensure admin user
init_db()
admin_user = os.environ.get("ADMIN_USER", "admin")
admin_pass = os.environ.get("ADMIN_PASS", "admin123")
if not find_user(admin_user):
    add_user(admin_user, admin_pass, role="admin")

# Register Blueprints
app.register_blueprint(web)
app.register_blueprint(api, url_prefix='/api')

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=True)
