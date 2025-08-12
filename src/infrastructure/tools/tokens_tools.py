from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import jwt
from loguru import logger


class TokensTypes(Enum):
    ACCESS: str = "access"
    REFRESH: str = "refresh"
    
    
class InvalidTokenType(Exception):
    ...


class InvalidToken(Exception):
    ...
    
    
class TokenExpired(Exception):
    ...
    

@dataclass
class JWTTokensGenerator:
    secret_key: str
    access_token_exp_minutes: int
    refresh_token_exp_minutes: int
    algorithm: str = "HS256"
        
    def _generate_jwt(self, payload: dict) -> str:
        return jwt.encode(
            payload=payload,
            key=self.secret_key,
            algorithm=self.algorithm
        )
        
    def _generate_token(
        self,
        sub: int | str,
        token_type: TokensTypes,
        expire_minutes: int
    ):
        current_timestamp = datetime.now()
        return self._generate_jwt(
            payload={
                "sub": str(sub),
                "token_type": token_type,
                "iat": int(current_timestamp.timestamp()),
                "exp": int((current_timestamp + timedelta(minutes=expire_minutes)).timestamp()),
            }
        )
        
    def generate_access_token(
        self,
        sub: str,
    ):
        return self._generate_token(
            sub=sub,
            token_type=TokensTypes.ACCESS.value,
            expire_minutes=self.access_token_exp_minutes
        )
        
    def generate_refresh_token(
        self,
        sub: int | str,
    ):
        return self._generate_token(
            sub=sub,
            token_type=TokensTypes.REFRESH.value,
            expire_minutes=self.refresh_token_exp_minutes
        )
        

@dataclass
class JWTTokensValidator:
    secret_key: str
    algorithm: str = "HS256"
    
    def _decode_jwt(self, token: str) -> dict:
        return jwt.decode(
            token,
            key=self.secret_key,
            algorithms=[self.algorithm],
        )
    
    def _validate_token(self, token: str, expected_token_type: TokensTypes) -> dict:
        try:
            payload = self._decode_jwt(token=token)
        except jwt.ExpiredSignatureError:
            raise TokenExpired
        except jwt.PyJWTError as ex:
            logger.error(f"{type(ex)}: {ex}")
            raise InvalidToken
        
        logger.debug(payload)
        if payload["token_type"] != expected_token_type.value:
            raise InvalidToken
        
        return payload
    
    def validate_access_token(self, token: str) -> dict:
        return self._validate_token(token=token, expected_token_type=TokensTypes.ACCESS)
    
    def validate_refresh_token(self, token: str) -> dict:
        return self._validate_token(token=token, expected_token_type=TokensTypes.REFRESH)
