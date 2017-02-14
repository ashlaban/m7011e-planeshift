import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import basedir

import wtforms_json
wtforms_json.init()

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

# Register blueprint(s)
from app.modules.controllers  import modules     as modules_mod
from app.modules.controllers  import module_api  as modules_api
from app.planes.controllers   import planes      as planes_mod
from app.planes.controllers   import planes_api  as planes_api
from app.profile.controllers  import profile     as profile_mod
app.register_blueprint(modules_mod)
app.register_blueprint(modules_api)
app.register_blueprint(planes_mod)
app.register_blueprint(planes_api)
app.register_blueprint(profile_mod)

from app import views, models
