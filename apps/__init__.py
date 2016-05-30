
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Instantiate Flask application:
app = Flask(__name__, template_folder="../templates",
            static_folder="../static")
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


from apps import views, models
