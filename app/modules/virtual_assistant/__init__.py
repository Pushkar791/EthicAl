from flask import Blueprint

bp = Blueprint('virtual_assistant', __name__, url_prefix='/assistant')

from app.modules.virtual_assistant import routes 