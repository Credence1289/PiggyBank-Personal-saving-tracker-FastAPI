from .dbengine import engine
from .db_models import Base

print("Creating Table......")
Base.metadata.create_all(bind = engine)
print("Table Created")