from flask import Blueprint
bp = Blueprint("progress", __name__)
from app.progress import routes
