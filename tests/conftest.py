from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

os.environ['AWS_ACCESS_KEY_ID'] = 'access_key_id'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'secret_access_key'
os.environ['AWS_DEFAULT_REGION'] = 'region'


def pytest_sessionstart(session):
    load_dotenv(Path(__file__).parent / '.env')
