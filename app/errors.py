import traceback
from fastapi import status


class AppError(Exception):
    def __init__(self, error_name, message, status_code, exc_traceback=None):
        self.error_name = error_name
        self.message = message
        self.status_code = status_code
        self.traceback = exc_traceback or traceback.format_exc()
        super().__init__(self.message)

    def __str__(self):
        return f"{self.error_name}: {self.message}"


class LoginError(AppError):
    def __init__(self):
        super().__init__(
            "LoginError", "A Login Error has occurred", status.HTTP_401_UNAUTHORIZED
        )


class MethodInputError(AppError):
    def __init__(self, message):
        super().__init__(
            "MethodInputError", message.strip(), status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class EmptyTokensError(AppError):
    def __init__(self):
        super().__init__(
            "EmptyTokensError", "Tokens are empty", status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class InvalidAccessTokenError(AppError):
    def __init__(self):
        super().__init__(
            "InvalidAccessTokenError",
            "An Invalid access token error was given, please try again",
            status.HTTP_401_UNAUTHORIZED,
        )


class InvalidRefreshTokenError(AppError):
    def __init__(self):
        super().__init__(
            "InvalidRefreshTokenError",
            "An Invalid refresh token error was given, please try again",
            status.HTTP_401_UNAUTHORIZED,
        )


class OTPCallbackNone(AppError):
    def __init__(self):
        super().__init__(
            "OTPCallbackNone",
            "A Wealthsimple OTP user account was triggered, please use a callback function",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class WSOTPError(AppError):
    def __init__(self):
        super().__init__(
            "WSOTPError",
            "Otp is null, try again with your authenticating method",
            status.HTTP_400_BAD_REQUEST,
        )


class WSOTPLoginError(AppError):
    def __init__(self):
        super().__init__(
            "WSOTPLoginError",
            "A Wealthsimple OTP login error happened, please try again",
            status.HTTP_400_BAD_REQUEST,
        )


class TSXStopLimitPriceError(AppError):
    def __init__(self):
        super().__init__(
            "TSXStopLimitPriceError",
            "TSX/TSX-V securities must have an equivalent stop and limit price",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class WealthsimpleServerError(AppError):
    def __init__(
        self, message="Wealthsimple endpoint might be down: return a 5XX HTTP code"
    ):
        super().__init__(
            "WealthsimpleServerError", message, status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class RouteNotFoundException(AppError):
    def __init__(self):
        super().__init__(
            "RouteNotFoundException",
            "Wealthsimple endpoint not found: return a 404 HTTP code",
            status.HTTP_404_NOT_FOUND,
        )


class WealthsimpleDownException(AppError):
    def __init__(self, message):
        super().__init__(
            "WealthsimpleDownException",
            message.strip(),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
