# settings.py
import os
from dotenv import load_dotenv, find_dotenv

from pathlib import Path  # Python 3.6+ only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

DISCORD_API_KEY = os.environ.get("DISCORD_API_KEY")
ROOT_PHOTO_FILE_ID = os.environ.get("ROOT_PHOTO_FILE_ID")
