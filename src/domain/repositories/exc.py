from dataclasses import dataclass


@dataclass
class CustomRepoException(Exception):
    message: str
    
    
@dataclass
class UserNotFound(CustomRepoException):
    message: str = "User not found"
    
    
@dataclass
class RefreshTokenNotFound(CustomRepoException):
    message: str = "Refresh token not found"
