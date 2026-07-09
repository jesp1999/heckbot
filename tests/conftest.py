from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


def pytest_sessionstart(session):
    load_dotenv(Path(__file__).parent / '.env')
