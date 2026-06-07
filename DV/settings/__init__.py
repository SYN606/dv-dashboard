from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")
env = os.getenv("DJANGO_ENV", "dev").lower()

if env == "prod":
    from .prod import *
else:
    from .dev import *
