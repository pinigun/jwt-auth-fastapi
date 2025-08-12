from fastapi import APIRouter, FastAPI
from .v1.auth.routes import router as auth_router
from .v1.users.routes import router as users_router


app = FastAPI()
api = FastAPI()

v1_router = APIRouter(prefix='/v1')
v1_router.include_router(auth_router)
v1_router.include_router(users_router)

api.include_router(v1_router)

app.mount('/api', api, 'API')
