import os
from sqlmodel import create_engine

# No fallback—forces explicit env setup
DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, echo=True)
