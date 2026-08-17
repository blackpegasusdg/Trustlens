import os

from flask import Flask
from flask_login import LoginManager

from .database import init_db
from .models import User


def create_app():

    app = Flask(__name__)

    # --------------------------------------------------
    # Configuration
    # --------------------------------------------------

    base_dir = os.path.abspath(
        os.path.dirname(__file__)
    )

    database_path = os.path.join(
        base_dir,
        "trustlens_social.db"
    )

    app.config["SECRET_KEY"] = "trustlens-demo-secret"

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + database_path
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --------------------------------------------------
    # Database
    # --------------------------------------------------

    init_db(app)

    # --------------------------------------------------
    # Login manager
    # --------------------------------------------------

    login_manager = LoginManager()

    login_manager.login_view = "login"

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --------------------------------------------------
    # Routes
    # --------------------------------------------------

    from .routes import social_bp

    app.register_blueprint(social_bp)

    return app


if __name__ == "__main__":

    app = create_app()

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )