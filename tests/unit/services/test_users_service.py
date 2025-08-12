import pytest
from unittest.mock import AsyncMock, create_autospec

from src.services.exc import UserNotFound
from src.services.users.dto import UserDTO
from src.services.users.service import UsersService
from src.domain.repositories.exc import UserNotFound as UserNotFoundDB
from src.domain.entities.users import User
from src.domain.repositories.users.interface import IUsersRepo
from src.domain.uof.abstract import IUnitOfWork


class MockData:
    EMAIL:              str = "test@email.com"
    PASSWORD:           str = "password"
    HASHED_PASSWORD:    str = "hashed_password"
    ID:                 int = 1


class MockUnitOfWork(IUnitOfWork):
    def __init__(
        self,
        users_repo,
    ):
        self._users = users_repo

    @property
    def users(self,):
        return self._users
    
    async def commit(self,):
        ...
    
    async def rollback(self,):
        ...
    
    async def __aenter__(self,) -> "IUnitOfWork":
        return self
    

@pytest.fixture
def users_repo_mock():
    return create_autospec(IUsersRepo, instance=True)


@pytest.fixture
def users_service(users_repo_mock):
    mock_uow = MockUnitOfWork(users_repo=users_repo_mock)
    return UsersService(
        unit_of_work=mock_uow,
    )


@pytest.mark.asyncio
async def test_get_user_success(
    users_service: UsersService,
    users_repo_mock,
):
    users_repo_mock.get_by_id = AsyncMock(
        return_value=User(
            id=MockData.ID,
            email=MockData.EMAIL,
            password_hash=MockData.HASHED_PASSWORD
        )
    )
    
    user = await users_service.get_user(
        id=MockData.ID,
    )
    
    assert user == UserDTO(
        id=MockData.ID,
        email=MockData.EMAIL,
    )
    
    
@pytest.mark.asyncio
async def test_get_user_not_found(
    users_service: UsersService,
    users_repo_mock,
):
    users_repo_mock.get_by_id = AsyncMock(
        side_effect=UserNotFoundDB
    )
    
    with pytest.raises(UserNotFound):
        await users_service.get_user(
            id=MockData.ID,
        )
