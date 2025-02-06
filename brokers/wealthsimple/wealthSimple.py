import cloudscraper
from datetime import datetime, timedelta
from loguru import logger
from typing import Optional, Union
from urllib.error import HTTPError

from .tokens import TokensBox
from .redis_cache import set_instance_cache
from .wsimple_requestor import requestor
from errors import InvalidRefreshTokenError, LoginError, WSOTPError
from .endpoints import Endpoints


class wealthSimple:
    BASE_URL = Endpoints.BASE.value
    BASE_PUBLIC_URL = Endpoints.BASE_PUBLIC.value
    BASE_STATUS_URL = Endpoints.BASE_STATUS.value

    time_ranges = ["1d", "1w", "1m", "3m", "1y", "all"]

    def __init__(
        self,
        email: str,
        password: str,
        mfa_code: int = None,
        oauth_mode: bool = False,
        tokens: Optional[list] = None,
        internally_manage_tokens: bool = True,
        two_factor_callback: callable = None,
    ):

        self.oauth_mode = oauth_mode
        self.internally_manage_tokens = internally_manage_tokens
        self.email = email
        self.logger = logger
        self.session = self.session = cloudscraper.create_scraper()

        if self.oauth_mode:
            print("Mode: Oauth (Bypass)")
            self.tokens = tokens

        # self.APIMAIN = "https://trade-service.wealthsimple.com/"
        # self.TradeAPI = APIRequestor(self.session, self.APIMAIN)
        self.wsimple_login(
            email,
            password,
            mfa_code,
            oauth_mode,
            internally_manage_tokens,
            two_factor_callback,
        )
        return None

    def wsimple_login(
        self,
        email: str,
        password: str,
        mfa_code: int = None,
        oauth_mode: bool = False,
        internally_manage_tokens: bool = True,
        two_factor_callback: callable = None,
    ):

        payload = {"email": email, "password": password}
        initial_request = requestor(
            endpoint=Endpoints.LOGIN,
            args={"base": self.BASE_URL},
            session=self.session,
            login_refresh=True,
            json=payload,
            logger=self.logger,
        )
        print(
            f"Pre-login: {initial_request.status_code}/ {str(initial_request.content)}"
        )
        print("is OTP Required")
        print("x-wealthsimple-otp-required" in initial_request.headers)
        if "x-wealthsimple-otp-required" in initial_request.headers:
            self.device_id = initial_request.headers["x-ws-device-id"]
            otp_headers = (
                initial_request.headers["x-wealthsimple-otp"]
                .replace(" ", "")
                .split(";")
            )
            method = otp_headers[1][7:]
            self._otp_info = {
                "required": (otp_headers[0]),
                "method": otp_headers[1][7:],
            }
            if mfa_code is None:
                raise WSOTPError()

            elif method == "sms":
                self._otp_info["digits"] = otp_headers[2][7:]
            print(f"EndPoint Requestor {Endpoints.LOGIN}")
            print("weathSimple payload")
            print(payload)
            payload["otp"] = mfa_code
            final_request = requestor(
                Endpoints.LOGIN,
                args={"base": self.BASE_URL},
                login_refresh=True,
                session=self.session,
                json=payload,
                logger=self.logger,
            )
            del payload
            #! natural code login\
            if final_request.status_code == 200:
                if self.internally_manage_tokens:
                    self.session.headers["Authorization"] = (
                        f"Bearer {final_request.headers['X-Access-Token']}"
                    )
                    self.box = TokensBox(
                        final_request.headers["X-Access-Token"],
                        final_request.headers["X-Refresh-Token"],
                        datetime.fromtimestamp(
                            int(final_request.headers["X-Access-Token-Expires"])
                        ),
                    )

                    return self
                else:
                    self.access_token = final_request.headers["X-Access-Token"]
                    self.refresh_token = final_request.headers["X-Refresh-Token"]
                    self.tokens = [
                        {"Authorization": self.access_token},
                        {"refresh_token": self.refresh_token},
                    ]
                self.data = final_request.json()
                set_instance_cache(self.box.access_token, self, self.box.access_expires)
                del final_request
                return self
            else:
                print(final_request.json())
                raise LoginError
        elif initial_request.status_code == 200:
            return self
        else:
            print(initial_request.json())
            del initial_request
            raise LoginError

    @classmethod
    def oauth_login(cls, token_dict, verbose=False):
        """
        constructor: login with a predefined list of tokens:
        """
        wsimple = cls("", "", oauth_mode=True, tokens=token_dict, verbose_mode=verbose)
        return wsimple

    def refresh_token(self, tokens=None):
        """
        Generates and applies a new set of access and refresh tokens.
        """
        r = requestor(
            Endpoints.REFRESH,
            args={"base": self.BASE_URL},
            data=tokens[1],
            login_refresh=True,
            logger=self.logger,
        )
        if r.status_code == 401:
            self.logger.error("Dead refresh token")
            raise InvalidRefreshTokenError
        else:
            if self.internally_manage_tokens:
                return TokensBox(
                    r.headers["X-Access-Token"],
                    r.headers["X-Refresh-Token"],
                    datetime.fromtimestamp(int(r.headers["X-Access-Token-Expires"])),
                )
            else:
                self.access_token = r.headers["X-Access-Token"]
                self.refresh_token = r.headers["X-Refresh-Token"]
                self.tokens = [
                    {"Authorization": self.access_token},
                    {"refresh_token": self.refresh_token},
                ]
                return self.tokens

    def _manage_tokens(f):
        def wrap_manage_tokens(self, *args, **kwargs):
            print(f"Tokens: {self.box} {args} {kwargs}")
            if self.internally_manage_tokens:
                diff = self.box.access_expires - datetime.now()
                print(f"Reset in -> {diff}")
                if diff < timedelta(minutes=15):
                    print("Resetting Tokens")
                    self.box = self.refresh_token(tokens=self.box.tokens)
                    print("Refreshed Tokens")
                    print(self.box)
                    set_instance_cache(
                        self.box.access_token, self, self.box.access_expires
                    )
                return f(self, *args, **kwargs)
            else:
                return f(self, *args, **kwargs)

        return wrap_manage_tokens

    def login(
        self,
        email: str = None,
        password: str = None,
        mfa_code: str = None,
        two_factor_callback: callable = None,
    ) -> None:

        if not email or not password:
            return {"status": 400, "error": "Missing login credentials"}

        # Login credentials to pass in request
        data = [("email", email), ("password", password)]

        try:
            # Initial login request
            response = self.TradeAPI.makeRequest("POST", "auth/login", data)
            print(response["x-wealthsimple-otp-required"])
            # Handle potential MFA requirement
            if "x-wealthsimple-otp" in response.headers:
                if not mfa_code and not two_factor_callback:
                    return {
                        "status": 403,
                        "error": "This account requires 2FA. Provide MFA code or a callback function.",
                    }

                otp_value = mfa_code or two_factor_callback()

                if not otp_value:
                    return {
                        "status": 403,
                        "error": "MFA code is required but not provided.",
                    }

                data.append(("otp", otp_value))
                response = self.TradeAPI.makeRequest("POST", "auth/login", data)

            # Check for invalid login
            if response.status_code == 401:
                return {"status": 401, "error": "Invalid login credentials."}

            # Raise any other potential HTTP errors
            response.raise_for_status()

            # Update session headers with the API access token
            self.session.headers.update(
                {"Authorization": response.headers["X-Access-Token"]}
            )

            return {"status": 200, "message": "Wealthsimple Login successful"}

        except HTTPError as http_err:
            # Handle HTTP errors explicitly
            return {"status": response.status_code, "error": str(http_err)}

        except Exception as err:
            # Handle general errors
            return {"status": 500, "error": str(err)}

    def get_accounts(self) -> list:
        response = self.TradeAPI.makeRequest("GET", "account/list")
        response = response.json()
        response = response["results"]
        return response

    def get_security_groups(
        self, limit: int = 98, sec_id: Optional[str] = None
    ) -> list:

        callParams = {}

        if limit is not None:
            callParams["limit"] = limit
        if sec_id is not None:
            callParams["security_id"] = sec_id

        response = self.TradeAPI.makeRequest(
            "GET", "security-groups", params=callParams
        )
        response = response.json()
        response = response["results"]
        return response

    def get_account_ids(self) -> list:

        userAccounts = self.get_accounts()
        accountIDList = []
        for account in userAccounts:
            accountIDList.append(account["id"])
        return accountIDList

    def get_account(self, id: str) -> dict:

        userAccounts = self.get_accounts()
        for account in userAccounts:
            if account["id"] == id:
                return account
        raise NameError(f"{id} does not correspond to any account")

    def get_account_history(self, id: str, time: str = "all") -> dict:

        response = self.TradeAPI.makeRequest(
            "GET", f"account/history/{time}?account_id={id}"
        )
        response = response.json()
        if "error" in response:
            if response["error"] == "Record not found":
                raise NameError(f"{id} does not correspond to any account")

        return response

    @_manage_tokens
    def get_activities(
        self,
        tokens=None,
        limit: int = 99,
        type: Union[str, list] = "all",
        sec_id: Optional[str] = None,
        account_id: Union[str, list] = None,
    ) -> list:
        callParams = {}

        if not limit is None:
            callParams["limit"] = limit
        if not account_id is None:
            callParams["account_id"] = account_id
        if not type == "all":
            callParams["type"] = type
        if not sec_id is None:
            callParams["security_id"] = sec_id
        try:
            print("Tokens after activities call")
            print(self.box.tokens)
            response = requestor(
                endpoint=Endpoints.GET_ACTIVITIES,
                args={"base": self.BASE_URL},
                session=self.session,
                login_refresh=True,
                json=callParams,
            )
            # response = self.TradeAPI.makeRequest("GET", "account/activities", params=callParams)
            response.raise_for_status()
            response_data = response.json()
            print("Result Length")
            print(len(response_data["results"]))
            print(response_data)
            return {"status": response.status_code, "data": response_data["results"]}
        except HTTPError as http_err:
            print("HTTP ERROR")
            return {"status": response.status_code, "error": str(http_err)}

        except Exception as error:
            print("OBJECT ERROR")
            print(error)
            return {"status": 500, "error": str(error)}

    def get_orders(self, symbol: str = None) -> list:

        response = self.TradeAPI.makeRequest("GET", "orders")
        response = response.json()
        # Check if order must be filtered:
        if symbol:
            filteredOrders = []
            for order in response["results"]:
                if order["symbol"] == symbol:
                    filteredOrders.append(order)
            return filteredOrders
        else:
            return response

    def get_security(self, id: str) -> dict:

        response = self.TradeAPI.makeRequest("GET", f"securities/{id}")
        response = response.json()
        return response

    def get_securities_from_ticker(self, symbol: str) -> list:
        response = self.TradeAPI.makeRequest("GET", f"securities?query={symbol}")
        response = response.json()
        return response["results"]

    def get_positions(self, id: str) -> list:

        response = self.TradeAPI.makeRequest(
            "GET", f"account/positions?account_id={id}"
        )
        response = response.json()
        return response["results"]

    def get_deposits(self) -> list:

        response = self.TradeAPI.makeRequest("GET", "deposits")
        response = response.json()
        return response["results"]
