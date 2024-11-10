from app import app
from models import db

with app.app_context():
    db.drop_all()  # Drop all tables
    db.create_all()  # Recreate all tables with the updated schema
