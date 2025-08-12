from loguru import logger
from fastapi import APIRouter, Body, Depends, Form, HTTPException

from src.infrastructure.api.dependencies import AuthService, get_auth_service, verify_refresh_token
from src.infrastructure.api.v1.users.schemas import UserResponse
from src.infrastructure.api.v1.auth.schemas import TokensResponse
from src.services.exc import InvalidPassword, UserAlreadyRegistred, UserNotFound


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/login")
async def login(
    username: str = Body(),
    password: str = Body(),
    auth_service:   AuthService = Depends(get_auth_service),
) -> TokensResponse:
    try:
        new_tokens = await auth_service.login_user(email=username, password=password)
    except (UserNotFound, InvalidPassword) as ex:
        logger.error(ex.message)
        raise HTTPException(403, detail="Invalid email or password")
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(500)
    
    return TokensResponse(
        access_token=new_tokens.access_token,
        refresh_token=new_tokens.refresh_token,
    )
    

@router.post("/register")
async def register(
    email:          str = Body(),
    password:       str = Body(),
    auth_service:   AuthService = Depends(get_auth_service)
) -> UserResponse:
    try:
        new_user = await auth_service.register_user(
            email=email,
            password=password,
        )
    except UserAlreadyRegistred as ex:
        raise HTTPException(409, detail=ex.message)
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(500, detail="User registration failed")
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email
    )
    
    
@router.post("/refresh")
async def refresh_tokens(
    token_payload: dict = Depends(verify_refresh_token),
    auth_service: AuthService = Depends(get_auth_service)
) -> TokensResponse:
    new_tokens = await auth_service.refresh_tokens(user_id=int(token_payload['sub']))
    return TokensResponse(
        access_token=new_tokens.access_token,
        refresh_token=new_tokens.refresh_token,
    )
