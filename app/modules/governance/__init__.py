from flask import Blueprint

bp = Blueprint('governance', __name__, url_prefix='/governance')

from app.modules.governance import routes 