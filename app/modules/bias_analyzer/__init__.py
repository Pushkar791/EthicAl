from flask import Blueprint

bp = Blueprint('bias_analyzer', __name__, url_prefix='/bias_analyzer')

from app.modules.bias_analyzer import routes 