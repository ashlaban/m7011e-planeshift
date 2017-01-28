# Import flask dependencies
from flask import Blueprint, render_template, redirect, flash, url_for, g, request

from app import app

from app import db, util

# import sqlalchemy
# import collections
# import werkzeug
# import pathlib

# Define blueprints
profile     = Blueprint('profile_mod', __name__, url_prefix='/profile')
profile_api = Blueprint('profile_api', __name__, url_prefix='/api/profile')

# =============================================================================
# Frontend endpoints
# =============================================================================
@profile.route('/')
def show_profile_page():
	if not g.user.is_authenticated:
		return render_template('/403.html')

	user_data = g.user.get_public_data()

	return render_template('profile/index.html', user=user_data)