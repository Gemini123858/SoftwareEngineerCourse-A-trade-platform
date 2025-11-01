"""
包含所有管理员专属的操作。
"""
from typing import List
from src.data_manager import DataManager
from src.models import User, Item
from src.services.auth_service import AuthService

class AdminService:
    def __init__(self, data_manager: DataManager, auth_service: AuthService):
        self.data_manager = data_manager
        self.auth_service = auth_service
    
    def _verify_admin(self, session_id: str):
        """辅助方法，用于验证当前用户是否为管理员"""
        user = self.auth_service.get_user_from_session(session_id)
        if not user or not user.is_admin:
            raise PermissionError("You do not have permission to perform this action.")
        return user

    def get_all_users(self, session_id: str) -> List[User]:
        self._verify_admin(session_id)
        return self.data_manager.get_all('user')

    def get_all_items(self, session_id: str) -> List[Item]:
        self._verify_admin(session_id)
        return self.data_manager.get_all('item')

    def delete_user(self, session_id: str, user_id_to_delete: int) -> bool:
        admin_user = self._verify_admin(session_id)
        if admin_user.id == user_id_to_delete:
            raise ValueError("Admin cannot delete themselves.")

        users = self.data_manager.get_all('user')
        original_count = len(users)
        users = [u for u in users if u.id != user_id_to_delete]
        
        if len(users) < original_count:
            self.data_manager.save_all('user', users)
            return True
        return False # User not found

    def delete_item(self, session_id: str, item_id_to_delete: int) -> bool:
        self._verify_admin(session_id)
        
        items = self.data_manager.get_all('item')
        original_count = len(items)
        items = [i for i in items if i.id != item_id_to_delete]

        if len(items) < original_count:
            self.data_manager.save_all('item', items)
            return True
        return False # Item not found