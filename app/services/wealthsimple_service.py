import keyring
from typing import Optional, Callable, Any, List, Dict
from ws_api import (
    WealthsimpleAPI,
    WSAPISession,
    OTPRequiredException,
    LoginFailedException,
    ManualLoginRequired,
    UnexpectedException,
    CurlException,
    WSApiException,
)
from app.repositories.account_respository import AccountRepository
from app.repositories.security_repository import SecurityRepository
from app.repositories.activity_repository import ActivityRepository
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

KEYRING_SERVICE = "wealthsimple.api"


class WealthsimpleService:

    def __init__(
        self,
        account_repo: AccountRepository = None,
        activity_repo: ActivityRepository = None,
        security_repo: SecurityRepository = None,
        logger=None,
    ):
        self.logger = logger
        self._client = None
        self.account_repo = account_repo
        self.activity_repo = activity_repo
        self.security_repo = security_repo

    @staticmethod
    def _persist_session(session_json: str, username: str) -> None:
        keyring.set_password(f"{KEYRING_SERVICE}.{username}", "session", session_json)

    @staticmethod
    def _remove_session(username: str) -> None:
        """Remove invalid session from keyring to prevent future failures with same invalid session."""
        try:
            keyring.delete_password(f"{KEYRING_SERVICE}.{username}", "session")
            logger.info(f"Removed invalid session for user: {username}")
        except Exception as e:
            logger.warning(f"Failed to remove session from keyring: {e}")

    @staticmethod
    def _retrieve_session(username: str) -> Optional[WSAPISession]:
        session_json = keyring.get_password(f"{KEYRING_SERVICE}.{username}", "session")
        if session_json:
            return WSAPISession.from_json(session_json)
        return None

    def login(
        self,
        db: Session,
        username: str,
        password: str,
        otp_answer: Optional[str] = None,
    ) -> WSAPISession:
        """
        Login and store session in keyring. Raises if 2FA or credentials fail.
        """
        try:
            sess = WealthsimpleAPI.login(
                username,
                password,
                otp_answer,
                persist_session_fct=self._persist_session,
            )
            # Store session just in case of refresh/token update
            self._persist_session(sess.to_json(), username)
            return sess
        except OTPRequiredException as e:
            logger.warning("2FA code required for Wealthsimple login")
            raise e
        except LoginFailedException as e:
            logger.error(f"Wealthsimple login failed: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected Wealthsimple login failure: {e}")
            raise e

    def get_api(
        self, db: Session, username: str, ensure_valid_token: bool = True
    ) -> WealthsimpleAPI:
        """
        Get WealthsimpleAPI object from stored session. Validates/refreshes token if requested.
        Cleans up invalid sessions to prevent future failures with the same invalid session.
        """
        sess = self._retrieve_session(username)
        if not sess:
            logger.info(
                "No Wealthsimple API session found in keyring; login is required."
            )
            raise ManualLoginRequired("No saved session; login required.")

        try:
            api = WealthsimpleAPI.from_token(
                sess, persist_session_fct=self._persist_session, username=username
            )
            # Token fetch/refresh occurs on creation
            return api
        except ManualLoginRequired as e:
            logger.warning(
                "Wealthsimple API session not valid and cannot be refreshed. Cleaning up invalid session."
            )
            # Clean up the invalid session from keyring
            self._remove_session(username)
            raise ManualLoginRequired("Session expired or invalid. Please login again.")
        except (WSApiException, UnexpectedException, CurlException) as e:
            logger.exception("Failed to create WealthsimpleAPI from session.")
            raise e

    def get_accounts(
        self, db: Session, username: str, open_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch Wealthsimple accounts for the user.
        """
        try:
            api = self.get_api(db, username)
            accounts = api.get_accounts(open_only=open_only)
            return accounts
        except Exception as e:
            logger.exception("Error fetching accounts from Wealthsimple")
            raise e

    def get_account_balances(
        self, db: Session, username: str, account_id: str
    ) -> Dict[str, float]:
        """
        Fetch account balances by Wealthsimple account id.
        """
        try:
            api = self.get_api(db, username)
            return api.get_account_balances(account_id)
        except Exception as e:
            logger.exception("Error fetching account balances from Wealthsimple")
            raise e

    def get_activities(
        self, db: Session, username: str, account_id: str, how_many: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent activities/transactions for an account.
        """
        try:
            api = self.get_api(db, username)
            return api.get_activities(account_id, how_many=how_many)
        except Exception as e:
            logger.exception("Error fetching activities from Wealthsimple")
            raise e

    def get_identity_historical_financials(
        self,
        db: Session,
        username: str,
        account_ids: Optional[list] = None,
        currency: str = "CAD",
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical financials for the user's accounts.
        """
        try:
            api = self.get_api(db, username)
            return api.get_identity_historical_financials(
                account_ids or [], currency=currency
            )
        except Exception as e:
            logger.exception("Error fetching historical financials from Wealthsimple")
            raise e

    def search_security(
        self,
        db: Session,
        username: str,
        query: str,
    ) -> List[Dict[str, Any]]:
        """
        Search for a security by symbol or name.
        """
        try:
            api = self.get_api(db, username)
            return api.search_security(query)
        except Exception as e:
            logger.exception("Error searching for security in Wealthsimple")
            raise e

    def get_security_market_data(
        self, db: Session, username: str, security_id: str
    ) -> Dict[str, Any]:
        """
        Fetch market data for a security.
        """
        try:
            api = self.get_api(db, username)
            return api.get_security_market_data(security_id)
        except Exception as e:
            logger.exception("Error fetching security market data from Wealthsimple")
            raise e

    def get_account_historical_financials(
        self, db: Session, username: str, account_id: str, currency: str = "CAD"
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical financials for a single account.
        """
        try:
            api = self.get_api(db, username)
            return api.get_account_historical_financials(account_id, currency=currency)
        except Exception as e:
            logger.exception(
                "Error fetching account historical financials from Wealthsimple"
            )
            raise e

    # Add more methods as needed...


wealthsimple_service = WealthsimpleService()
