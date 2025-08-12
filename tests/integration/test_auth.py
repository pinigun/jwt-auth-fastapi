import asyncio
import pytest
import pytest_asyncio
from loguru import logger
from fastapi.datastructures import FormData
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.infrastructure.api.app import app, api
from src.infrastructure.database.models import Base
from src.infrastructure.api.dependencies import get_session_maker


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
)

sessionmaker_test = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest_asyncio.fixture
async def init_db():
    async with engine.begin() as conn:
        # создаём схему
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # чистим
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def get_test_session_maker():
    return sessionmaker_test


@pytest.fixture
def override_deps():
    app.dependency_overrides[get_session_maker] = get_test_session_maker
    api.dependency_overrides[get_session_maker] = get_test_session_maker
    app.mount('/api', api, 'API')

    
@pytest.fixture
def get_transport(init_db, override_deps):
    print(f"Overrides deps: {app.dependency_overrides.get(get_session_maker)}")
    transport = ASGITransport(app=app)
    return transport
        

# Основной тест
@pytest.mark.asyncio
async def test_full_auth_flow(get_transport):
    async with AsyncClient(transport=get_transport, base_url="http://test") as client:
        logger.debug("1. Register new user")

        email = "test_user@example.co"
        password = "securepassword123"

        register_data = {"email": email, "password": password}
        register_response = await client.post("/api/v1/auth/register", json=register_data)

        assert register_response.status_code == 200
        register_data = register_response.json()
        assert register_data["email"] == email
        assert "id" in register_data
        user_id = register_data["id"]

        logger.debug("2. Login by new user")
        login_form = {"username": email, "password": password}
        login_response = await client.post("/api/v1/auth/login", json=login_form)
        
        assert login_response.status_code == 200
        tokens = login_response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        logger.debug("3. Get authentithicated user info")
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = await client.get("/api/v1/users/me", headers=headers)
        
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["id"] == user_id
        assert me_data["email"] == email
        
        logger.debug("4. Refresh tokens")
        await asyncio.sleep(1)
        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        refresh_response = await client.post("/api/v1/auth/refresh", headers=refresh_headers)
        
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        new_access_token = new_tokens["access_token"]
        new_refresh_token = new_tokens["refresh_token"]
        
        assert new_access_token != access_token
        assert new_refresh_token != refresh_token
        
        logger.debug("5. Attempt to use an old refresh token (expecting an error)")
        expired_response = await client.post("/api/v1/auth/refresh", headers=refresh_headers)
        
        assert expired_response.status_code == 401
        error_detail = expired_response.json().get("detail", "")
        assert "invalid" in error_detail.lower() or "expired" in error_detail.lower()
        
        logger.debug("6. Obtaining Information with a New Access Token")
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        new_me_response = await client.get("/api/v1/users/me", headers=new_headers)
        
        assert new_me_response.status_code == 200
        new_me_data = new_me_response.json()
        assert new_me_data["id"] == user_id
        assert new_me_data["email"] == email
