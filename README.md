# Demo authorization service

## Introducing
It's a lightweight JWT-based authorization service demonstrating clean architecture and DDD principles. It includes core features like registration, email/password login, token refresh, and user info retrieval.

While the architectural approach might be more comprehensive than strictly necessary for this scope, I wanted to demonstrate my ability to implement these patterns effectively in a project.


Built with:

- Python (FastAPI, Pydantic, pytest, SQLAlchemy, pyjwt, alembic)
- PostgreSQL
- Docker for deployment


## Quick start
After cloning repo
```bash
cd jwt-auth-fastpi
docker-compose up --build -d
```


<details>
<summary>⚠️ If you have the same problem as me and your Python image is not downloading.</summary>

You should use a docker hub mirror in this format:

```bash
docker pull <mirror host>/python:3.12.11-slim-bullseye
```

It helped me
```bash
docker pull dh-mirror.gitverse.ru/python:3.12.11-slim-bullseye
```
</details>


After you can visit Swagger: `http://localhost:1602/api/docs`


##  Security Rules
- Access token lifetime: 1 minute (default)
- Refresh token lifetime: 5 minutes (default)
- Password storage: bcrypt hashing
- Refresh tokens are single-use


## Endpoints

### 🔐 Authentication

#### Register new user `POST /api/v1/auth/register`
> Register new user

_Request (JSON):_
```json
{
  "email": "user@example.com",
  "password": "your_password_123"
}
```

_Response 200_
```json
{
  "id": 1,
  "email": "user@example.com"
}
```


----


#### Login user `POST /api/v1/auth/login`

> Login user and returned pair of tokens

_Request (JSON):_
```json
{
  "email": "user@example.com",
  "password": "your_password_123"
}
```

_Response 200_
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
}
```


---


#### Refresh tokens `POST /api/v1/auth/refresh`

> Updating tokens with refresh token

_Headers:_
```http
Authorization: Bearer <refresh_token>
```

_Response 200_
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
}
```

---

### 👤 User

#### Get current user `POST /api/v1/auth/refresh`

> Updating tokens with refresh token

_Headers:_
```http
Authorization: Bearer <access_token>
```

_Response 200_
```json
{
  "id": 1,
  "email": "user@example.com",
}
```



### Tests
Test coverage:
```bash
pytest --cov src tests/
```
```bash
==================================================================== tests coverage =====================================================================
____________________________________________________ coverage: platform linux, python 3.12.3-final-0 ____________________________________________________

Name                                                Stmts   Miss  Cover
-----------------------------------------------------------------------
src/domain/entities/base.py                             5      1    80%
src/domain/entities/users.py                            9      0   100%
src/domain/repositories/exc.py                         10      0   100%
src/domain/repositories/users/interface.py              3      0   100%
src/domain/uof/abstract.py                              8      0   100%
src/infrastructure/api/app.py                          10      0   100%
src/infrastructure/api/dependencies.py                 58     16    72%
src/infrastructure/api/v1/auth/routes.py               32     14    56%
src/infrastructure/api/v1/auth/schemas.py               4      0   100%
src/infrastructure/api/v1/users/routes.py              12      3    75%
src/infrastructure/api/v1/users/schemas.py              4      0   100%
src/infrastructure/database/__init__.py                 7      2    71%
src/infrastructure/database/models.py                  13      0   100%
src/infrastructure/database/repositories/users.py      52     20    62%
src/infrastructure/database/uof.py                     25      1    96%
src/infrastructure/tools/password_manager.py           14      0   100%
src/infrastructure/tools/tokens_tools.py               48      6    88%
src/services/auth/dto.py                                7      1    86%
src/services/auth/service.py                           78     15    81%
src/services/exc.py                                    16      0   100%
src/services/users/dto.py                               7      1    86%
src/services/users/service.py                          21      3    86%
-----------------------------------------------------------------------
TOTAL                                                 443     83    81%
=================================================================== 8 passed in 4.04s ===================================================================
```
