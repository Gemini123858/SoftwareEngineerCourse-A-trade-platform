"""
负责用户认证、注册和会话管理。
"""
import uuid
from typing import Dict, Tuple
from src.data_manager import DataManager
from src.models import User

# 简单的内存会话存储。在真实应用中，这可能会用 Redis 等替代。
_SESSIONS: Dict[str, int] = {} # session_id -> user_id

class AuthService:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def register(self, email: str, password: str, nickname: str, contact_info: str) -> User:
        users = self.data_manager.get_all('user')
        if any(u.email == email for u in users):
            raise ValueError(f"Email '{email}' is already registered.")

        # 在真实项目中，这里必须进行哈希处理！
        # from werkzeug.security import generate_password_hash
        # password_hash = generate_password_hash(password)
        password_hash = f"hashed_{password}" # 简单模拟

        new_id = self.data_manager.get_new_id(users)
        new_user = User(
            id=new_id,
            email=email,
            password_hash=password_hash,
            nickname=nickname,
            contact_info=contact_info
        )
        users.append(new_user)
        self.data_manager.save_all('user', users)
        return new_user

    def login(self, email: str, password: str) -> Tuple[str, User]:
        users = self.data_manager.get_all('user')
        user = next((u for u in users if u.email == email), None)

        # 在真实项目中，这里要比对哈希值
        # from werkzeug.security import check_password_hash
        # if user and check_password_hash(user.password_hash, password):
        if user and user.password_hash == f"hashed_{password}":
            session_id = str(uuid.uuid4())
            _SESSIONS[session_id] = user.id
            return session_id, user
        
        raise ValueError("Invalid email or password.")

    def logout(self, session_id: str):
        if session_id in _SESSIONS:
            del _SESSIONS[session_id]
    
    def get_user_from_session(self, session_id: str) -> User | None:
        user_id = _SESSIONS.get(session_id)
        if not user_id:
            return None
        
        users = self.data_manager.get_all('user')
        return next((u for u in users if u.id == user_id), None)
