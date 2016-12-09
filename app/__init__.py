import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import basedir

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

# Register blueprint(s)
from app.modules.controllers import modules as modules_mod
from app.planes.controllers  import planes  as planes_mod
app.register_blueprint(modules_mod)
app.register_blueprint(planes_mod)

from app import views, models
