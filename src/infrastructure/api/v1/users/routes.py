from fastapi import APIRouter, Depends, HTTPException

from .schemas import UserResponse
from src.services.exc import UserNotFound
from src.infrastructure.api.dependencies import UsersService, get_users_service, verify_access_token


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
async def get_current_user(
    current_user:   dict = Depends(verify_access_token),
    users_service:  UsersService = Depends(get_users_service)
) -> UserResponse:
    try:
        user = await users_service.get_user(id=int(current_user["sub"]))
    except UserNotFound as ex:
        raise HTTPException(400, detail=ex.message)
    
    return UserResponse(
        id=user.id,
        email=user.email
    )
