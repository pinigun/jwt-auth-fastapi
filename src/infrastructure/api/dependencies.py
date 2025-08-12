from typing import Type
from loguru import logger
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from settings import settings
from src.domain.repositories.users.interface import IUsersRepo
from src.services.users.service import UsersService
from src.services.exc import RefreshTokenNotFound
from src.domain.uof.abstract import IUnitOfWork
from src.infrastructure.database import async_session_maker
from src.infrastructure.database.repositories.users import SqlAlchemyUsersRepo
from src.infrastructure.database.uof import SQLAlchemyUnitOfWork
from src.infrastructure.tools.tokens_tools import JWTTokensGenerator, JWTTokensValidator, InvalidToken,  TokenExpired
from src.infrastructure.tools.password_manager import PasswordManager
from src.services.auth.service import AuthService


bearer_access_token = HTTPBearer(scheme_name="Access token")
bearer_refresh_token = HTTPBearer(scheme_name="Refresh token")


def get_users_repo_class() -> Type[IUsersRepo]:
    return SqlAlchemyUsersRepo


def get_session_maker():
    return async_session_maker


def get_unit_of_work(
    session_maker=Depends(get_session_maker),
    users_repo_class=Depends(get_users_repo_class)
) -> IUnitOfWork:
    return SQLAlchemyUnitOfWork(
        async_session_maker=session_maker,
        users_repo_class=users_repo_class
    )


def get_auth_service(
    unit_of_work=Depends(get_unit_of_work)
) -> AuthService:
    return AuthService(
        unit_of_work=unit_of_work,
        password_manager=PasswordManager(),
        tokens_generator=JWTTokensGenerator(
            secret_key=settings.SECRET_KEY,
            access_token_exp_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_exp_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )
    )
    
    
def get_users_service(
    unit_of_work=Depends(get_unit_of_work)
) -> UsersService:
    return UsersService(
        unit_of_work=unit_of_work
    )
    
    
def verify_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_access_token)
) -> dict:
    try:
        access_token = credentials.credentials
        tokens_validator = JWTTokensValidator(
            secret_key=settings.SECRET_KEY,
        )
        
        logger.debug("Validate refresh token")
        payload = tokens_validator.validate_access_token(access_token)
    except TokenExpired:
        raise HTTPException(401, detail="TokenExpired")
    except InvalidToken:
        raise HTTPException(401, detail="Invalid token")
    except Exception as ex:
        logger.error(f"{type(ex)}: {ex}")
        raise HTTPException(500, detail="Internal server error")
    
    return payload


async def verify_refresh_token(
    credentials:    HTTPAuthorizationCredentials = Depends(bearer_refresh_token),
    auth_service:   AuthService = Depends(get_auth_service)
) -> dict:
    try:
        logger.debug("Extract credentials refresh token")
        refresh_token = credentials.credentials

        tokens_validator = JWTTokensValidator(
            secret_key=settings.SECRET_KEY,
        )
        
        logger.debug("Validate refresh token")
        payload = tokens_validator.validate_refresh_token(refresh_token)
        
        logger.debug(f"Checking refresh token in db User(id={payload['sub']}).")
        await auth_service.check_refresh_token(
            user_id=int(payload['sub']),
            refresh_token=refresh_token,
        )
    except TokenExpired:
        raise HTTPException(401, detail="Token expired")
    except (InvalidToken, RefreshTokenNotFound):
        raise HTTPException(401, detail="Invalid token")
    except Exception as ex:
        logger.error(f"{type(ex)}: {ex}")
        raise HTTPException(500, detail="Internal server error")
    
    return payload
