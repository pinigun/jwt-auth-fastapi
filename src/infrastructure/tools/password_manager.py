import bcrypt
from dataclasses import dataclass


@dataclass
class PasswordManager:
    rounds: int = 12
      
    def hash_password(self, password: str) -> str:
        password_bytes = password.encode('utf-8')
        
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(password_bytes, hashed_bytes)
