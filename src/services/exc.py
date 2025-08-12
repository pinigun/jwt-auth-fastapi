from dataclasses import dataclass


@dataclass
class CustomServicesException(Exception):
    message: str


@dataclass
class UserAlreadyRegistred(CustomServicesException):
    message: str = "User already registred"


@dataclass
class UserNotFound(CustomServicesException):
    message: str = "User not found"


@dataclass
class RefreshTokenNotFound(CustomServicesException):
    message: str = "Refresh token not found"


@dataclass
class InvalidPassword(CustomServicesException):
    message: str = "Invalid password"
