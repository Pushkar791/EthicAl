from app import create_app, db
from app.models import *  # Import all models for migration to detect

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True) 