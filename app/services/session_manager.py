import keyring
from typing import Optional
from ws_api import WSAPISession

SERVICE_KEY = "pytrade-wealthsimple"


def persist_session(session_json: str):
    keyring.set_password(SERVICE_KEY, "session", session_json)


def load_session() -> Optional[WSAPISession]:
    session_data = keyring.get_password(SERVICE_KEY, "session")
    return WSAPISession.from_json(session_data) if session_data else None


def clear_session():
    keyring.delete_password(SERVICE_KEY, "session")
