import pytest
from unittest.mock import AsyncMock, Mock, create_autospec

from src.domain.entities.users import User
from src.services.auth.dto import TokensDTO
from src.domain.uof.abstract import IUnitOfWork
from src.services.auth.service import AuthService
from src.domain.repositories.users.interface import IUsersRepo
from src.infrastructure.tools.tokens_tools import JWTTokensGenerator
from src.infrastructure.tools.password_manager import PasswordManager
from src.domain.repositories.exc import UserNotFound as UserNotFoundDB
from src.services.exc import UserAlreadyRegistred, UserNotFound, InvalidPassword


class MockData:
    EMAIL: str = "test@email.com"
    PASSWORD: str = "password"
    
    ACCESS_TOKEN: str = "access_token"
    REFRESH_TOKEN: str = "refresh_token"
    HASHED_PASSWORD: str = "hashed_password"
    

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
def tokens_generator_mock():
    tgm = create_autospec(JWTTokensGenerator, instance=True)
    tgm.generate_refresh_token = Mock(return_value=MockData.REFRESH_TOKEN)
    tgm.generate_access_token = Mock(return_value=MockData.ACCESS_TOKEN)
    return tgm


@pytest.fixture
def password_manager_mock():
    pmm = create_autospec(PasswordManager, instance=True)
    pmm.hash_password = Mock(return_value=MockData.HASHED_PASSWORD)
    return pmm


@pytest.fixture
def auth_service(users_repo_mock, password_manager_mock, tokens_generator_mock):
    mock_uow = MockUnitOfWork(users_repo=users_repo_mock)
    return AuthService(
        unit_of_work=mock_uow,
        password_manager=password_manager_mock,
        tokens_generator=tokens_generator_mock,
    )


@pytest.mark.asyncio
async def test_login_user_success(
    auth_service: AuthService,
    users_repo_mock,
):
    users_repo_mock.get_by_email = AsyncMock(
        return_value=User(
            id=1,
            email=MockData.EMAIL,
            password_hash=MockData.HASHED_PASSWORD
        )
    )
    
    new_tokens_data = await auth_service.login_user(
        email=MockData.EMAIL,
        password=MockData.PASSWORD
    )
    
    assert new_tokens_data == TokensDTO(
        access_token=MockData.ACCESS_TOKEN,
        refresh_token=MockData.REFRESH_TOKEN
    )

        
@pytest.mark.asyncio
async def test_login_user_invalid_password(
    auth_service: AuthService,
    users_repo_mock,
    password_manager_mock,
):
    users_repo_mock.get_by_email = AsyncMock(
        return_value=User(
            id=1,
            email=MockData.EMAIL,
            password_hash=MockData.HASHED_PASSWORD
        )
    )
    password_manager_mock.verify_password = Mock(return_value=False)
    
    with pytest.raises(InvalidPassword):
        await auth_service.login_user(
            email=MockData.EMAIL,
            password=MockData.PASSWORD
        )
        
    
@pytest.mark.asyncio
async def test_login_user_not_found_user(
    auth_service: AuthService,
    users_repo_mock,
):
    users_repo_mock.get_by_email = AsyncMock(
        side_effect=UserNotFoundDB
    )
    
    with pytest.raises(UserNotFound):
        await auth_service.login_user(
            email=MockData.EMAIL,
            password=MockData.PASSWORD
        )
        
        
@pytest.mark.asyncio
async def test_register_user_success(
    auth_service: AuthService,
    users_repo_mock,
):
    users_repo_mock.get_by_email = AsyncMock(side_effect=UserNotFoundDB)
    users_repo_mock.add_user = AsyncMock(
        return_value=User(
            id=1,
            email=MockData.EMAIL,
            password_hash=MockData.HASHED_PASSWORD
        )
    )
        
    new_user = await auth_service.register_user(
        email=MockData.EMAIL,
        password=MockData.PASSWORD
    )

    assert new_user == User(
        id=1,
        email=MockData.EMAIL,
        password_hash=MockData.HASHED_PASSWORD
    )
    
    
@pytest.mark.asyncio
async def test_register_user_already_registred(
    auth_service: AuthService,
    users_repo_mock,
):
    users_repo_mock.get_by_email = AsyncMock(
        return_value=User(
            id=1,
            email=MockData.EMAIL,
            password_hash=MockData.HASHED_PASSWORD
        )
    )
    
    with pytest.raises(UserAlreadyRegistred):
        await auth_service.register_user(
            email=MockData.EMAIL,
            password=MockData.PASSWORD
        )
