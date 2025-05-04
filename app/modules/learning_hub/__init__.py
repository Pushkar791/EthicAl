from flask import Blueprint

bp = Blueprint('learning_hub', __name__, url_prefix='/learning')

from app.modules.learning_hub import routes 