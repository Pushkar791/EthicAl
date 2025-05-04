from app import create_app, db
from app.models import BiasReport, BiasRecommendation
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Add columns to the BiasReport table
    db.session.execute(text('ALTER TABLE bias_report ADD COLUMN visualizations JSON'))
    db.session.execute(text('ALTER TABLE bias_report ADD COLUMN explainability JSON'))
    
    # Add column to the BiasRecommendation table
    db.session.execute(text('ALTER TABLE bias_recommendation ADD COLUMN action_items JSON'))
    
    # Commit the changes
    db.session.commit()
    
    print('Database updated successfully!') 