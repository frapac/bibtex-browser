
from flask import Flask
from flask.ext.login import LoginManager

# Instantiate Flask application:
app = Flask(__name__, template_folder="../templates",
            static_folder="../static")
app.config.from_object('config')
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


from apps import views
