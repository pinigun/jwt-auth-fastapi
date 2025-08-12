from dataclasses import dataclass

from loguru import logger
from src.domain.entities.users import User
from src.domain.repositories.exc import (
    UserNotFound as UserNotFoundDB,
    RefreshTokenNotFound as RefreshTokenNotFoundDB,
)

from src.domain.uof.abstract import IUnitOfWork
from src.infrastructure.tools.tokens_tools import JWTTokensGenerator
from src.infrastructure.tools.password_manager import PasswordManager

from .dto import TokensDTO
from ..exc import InvalidPassword, UserAlreadyRegistred, UserNotFound, RefreshTokenNotFound


@dataclass
class AuthService:
    unit_of_work: IUnitOfWork
    
    # NOTE: PasswordManager is intentionally used without abstraction
    # as it's pure infrastructure concern with low change probability.
    # YAGNI principle applied for interface abstraction.
    password_manager: PasswordManager
    
    # NOTE: We intentionally avoid abstraction for token operations to reduce complexity.
    # Given the low probability of changing token mechanisms (JWT → other) and the fact
    # that such change would require significant overhaul regardless of abstraction layers,
    # we favor simplicity and direct implementation here.
    #
    # Trade-offs:
    # - (+) Removes abstraction overhead and indirection
    # - (+) Reduces cognitive load for maintainers
    # - (-) Would require service-layer modifications if token technology changes
    #
    # Rationale: YAGNI principle.
    tokens_generator: JWTTokensGenerator
    
    async def login_user(
        self,
        email:      str,
        password:   str,
    ) -> TokensDTO:
        try:
            logger.debug(f"Trying find user with email='{email}' in database")
            async with self.unit_of_work as uof:
                user = await uof.users.get_by_email(
                    email=email,
                )
                
                is_valid_password = self.password_manager.verify_password(password, user.password_hash)
                logger.debug(f"{is_valid_password=}")
                if not is_valid_password:
                    logger.debug(f"User(email='{email}') invalid password")
                    raise InvalidPassword
                
                logger.debug("Generating pair of JWT-tokens")
                refresh_token = self.tokens_generator.generate_refresh_token(sub=user.id)
                access_token = self.tokens_generator.generate_access_token(sub=user.id)
                
                try:
                    logger.debug(f"Try update refresh token User(id={user.id})")
                    await uof.users.update_refresh_token(
                        user_id=user.id,
                        refresh_token=refresh_token
                    )
                except RefreshTokenNotFoundDB:
                    logger.debug(f"Refresh token not found User(id={user.id})")
                    logger.debug(f"Add refresh token User(id={user.id})")
                    await uof.users.add_refresh_token(
                        user_id=user.id,
                        refresh_token=refresh_token
                    )
                    
        except UserNotFoundDB:
            logger.debug(f"User email='{email}' not found")
            raise UserNotFound
        
        except Exception as ex:
            logger.error(f"User login failed User(email='{email}'). Error: {type(ex)}: {str(ex)}")
            raise ex
                
        logger.info(f"Login user with email='{email}'.")
        return TokensDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    async def register_user(
        self,
        email:      str,
        password:   str,
    ) -> User:
        try:
            logger.debug(f"Trying find User(email='{email}') in database.")
            async with self.unit_of_work as uof:
                await uof.users.get_by_email(
                    email=email
                )
        except UserNotFoundDB:
            try:
                logger.debug(f"Register User(email='{email}').")
                
                async with self.unit_of_work as uof:
                    logger.debug(f"Adding User(email='{email}').")
                    new_user = await uof.users.add_user(
                        user=User(
                            id=0,
                            email=email,
                            password_hash=self.password_manager.hash_password(password)
                        )
                    )
                                        
                    logger.info(f"New User(email='{email}') succesfully added.")
                    return User(
                        id=new_user.id,
                        email=new_user.email,
                        password_hash=new_user.password_hash
                    )
            except Exception as ex:
                logger.error(f"User registration failed User(email='{email}'. Error: {str(ex)})")
                raise ex
        else:
            logger.debug(f"User(email='{email}') already registred.")
            raise UserAlreadyRegistred
        
    async def check_refresh_token(self, user_id: int, refresh_token: str):
        async with self.unit_of_work as uof:
            db_refresh_token = await uof.users.get_refresh_token(
                user_id=user_id
            )
            
        if not db_refresh_token == refresh_token:
            raise RefreshTokenNotFound
        
    async def refresh_tokens(self, user_id: int) -> TokensDTO:
        logger.debug("Generating pair of JWT-tokens")
        refresh_token = self.tokens_generator.generate_refresh_token(sub=user_id)
        access_token = self.tokens_generator.generate_access_token(sub=user_id)
        
        try:
            async with self.unit_of_work as uof:
                await uof.users.update_refresh_token(
                    user_id=user_id,
                    refresh_token=refresh_token
                )
        except RefreshTokenNotFoundDB:
            raise RefreshTokenNotFound
        except Exception as ex:
            logger.error(f"{type(ex)}: {ex}")
            raise ex
        
        return TokensDTO(
            refresh_token=refresh_token,
            access_token=access_token
        )
