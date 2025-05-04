from app import create_app, db
from app.models import *  # Import all models for migration

app = create_app()

# Initialize database tables if needed
with app.app_context():
    db.create_all()
    
# This is the handler that Vercel will use
def handler(request, **kwargs):
    return app(request.environ, request.start_response) 