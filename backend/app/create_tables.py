# backend/app/create_tables.py

from app.db.session import Base, engine
from app.db import models  # Ensure all models are imported

Base.metadata.create_all(bind=engine)
print("✅ Tables created.")
