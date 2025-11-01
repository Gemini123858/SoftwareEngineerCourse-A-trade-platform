"""
数据管理器，负责所有与 JSON 文件的读写操作。
这是项目的持久化层，将业务逻辑与文件 IO 分离。
"""

import json
import os
from typing import List, Dict, Any, TypeVar, Type
from . import models

# 定义一个泛型类型变量，用于类型提示
T = TypeVar('T')

class DataManager:
    def __init__(self, data_folder: str = "data"):
        self.data_folder = data_folder
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        self.users_file = os.path.join(self.data_folder, "users.json")
        self.items_file = os.path.join(self.data_folder, "items.json")
        self.interactions_file = os.path.join(self.data_folder, "interactions.json")

    def _read_data(self, file_path: str) -> List[Dict[str, Any]]:
        """通用的读取 JSON 文件方法"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_data(self, file_path: str, data: List[Dict[str, Any]]):
        """通用的写入 JSON 文件方法"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _load_objects(self, file_path: str, model_class: Type[T]) -> List[T]:
        """从文件加载数据并转换为模型对象列表"""
        data = self._read_data(file_path)
        return [model_class(**d) for d in data]

    def _save_objects(self, file_path: str, objects: List[Any]):
        """将模型对象列表转换为字典并写入文件"""
        data = [obj.__dict__ for obj in objects]
        self._write_data(file_path, data)
        
    def _generate_new_id(self, objects: List[Any]) -> int:
        """根据现有对象列表生成一个新的唯一 ID"""
        if not objects:
            return 1
        return max(obj.id for obj in objects) + 1

    # --- 用户管理 ---
    def get_all_users(self) -> List[models.User]:
        return self._load_objects(self.users_file, models.User)

    def get_user_by_id(self, user_id: int) -> models.User | None:
        for user in self.get_all_users():
            if user.id == user_id:
                return user
        return None
        
    def get_user_by_email(self, email: str) -> models.User | None:
        for user in self.get_all_users():
            if user.email == email:
                return user
        return None

    def save_user(self, user: models.User):
        """保存单个用户（新增或更新）"""
        users = self.get_all_users()
        # 如果用户已存在，则替换；否则添加
        user_exists = False
        for i, u in enumerate(users):
            if u.id == user.id:
                users[i] = user
                user_exists = True
                break
        if not user_exists:
            users.append(user)
        self._save_objects(self.users_file, users)
        
    def get_new_user_id(self) -> int:
        return self._generate_new_id(self.get_all_users())

    # --- 商品管理 ---
    def get_all_items(self) -> List[models.Item]:
        return self._load_objects(self.items_file, models.Item)

    def get_item_by_id(self, item_id: int) -> models.Item | None:
        for item in self.get_all_items():
            if item.id == item_id:
                return item
        return None

    def save_item(self, item: models.Item):
        items = self.get_all_items()
        item_exists = False
        for i, it in enumerate(items):
            if it.id == item.id:
                items[i] = item
                item_exists = True
                break
        if not item_exists:
            items.append(item)
        self._save_objects(self.items_file, items)
        
    def get_new_item_id(self) -> int:
        return self._generate_new_id(self.get_all_items())

    # --- 交互记录管理 ---
    def get_all_interactions(self) -> List[models.InterestInteraction]:
        return self._load_objects(self.interactions_file, models.InterestInteraction)

    def save_interaction(self, interaction: models.InterestInteraction):
        interactions = self.get_all_interactions()
        interactions.append(interaction) # 交互记录只增不改
        self._save_objects(self.interactions_file, interactions)
        
    def get_new_interaction_id(self) -> int:
        return self._generate_new_id(self.get_all_interactions())