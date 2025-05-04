from app import create_app, db
from app.models import *  # Import all models for migration

app = create_app()

# This is important for Vercel serverless
def handler(request, **kwargs):
    try:
        # For first run only, try to create tables
        # This may fail if the app is already created, which is fine
        if request.get('path', '') == '/':
            with app.app_context():
                try:
                    db.create_all()
                except:
                    pass  # Silently continue if tables already exist
    except:
        pass  # Fail silently if there are issues

    return app(request.environ, request.start_response) 