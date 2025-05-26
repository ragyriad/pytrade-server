import json
import cloudscraper as req
from loguru import logger
from box import Box
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, Timeout

# errors
from app.errors import (
    InvalidAccessTokenError,
    WealthsimpleServerError,
    RouteNotFoundException,
    LoginError,
)


def requestor(
    endpoint,
    args,
    logger=None,
    request_status=False,
    response_list=False,
    retry_strategy=None,
    session=None,
    login_refresh=False,
    **kwargs,
) -> Box:
    try:
        if session is None:
            session = req.create_scraper()
        if retry_strategy is None:
            default_retry_strategy = Retry(
                total=1,  # Number of retries
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=[
                    "HEAD",
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE",
                    "OPTIONS",
                    "TRACE",
                ],
                backoff_factor=1,  # Wait between retries
            )
        adapter = HTTPAdapter(max_retries=default_retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        name: str = endpoint.name
        url: str = endpoint.value.route.format(**args)
        print("Requestor Call")
        print(url)
        print(kwargs)
        r = session.request(method=endpoint.value[1], url=url, **kwargs)
        if login_refresh:
            return r
        if r.status_code == 400:
            raise LoginError
        if r.status_code == 401:
            raise InvalidAccessTokenError
        elif r.status_code == 404:
            print(f"404 on {r.url}")
            raise RouteNotFoundException
        elif r.status_code >= 500:
            raise WealthsimpleServerError
        else:
            if request_status:
                return Box(json.loads(r.content))
            elif response_list:
                return Box(r.json()[0])
            else:
                return Box(r.json())

    except (ConnectionError, ConnectionResetError) as e:
        print(f"Connection error occurred: {str(e)}")
        raise WealthsimpleServerError()

    except Timeout as e:
        print(f"Request timed out: {str(e)}")
        raise WealthsimpleServerError()
