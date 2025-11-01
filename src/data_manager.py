"""
数据管理器，负责所有与 JSON 文件的读写操作。
"""

import json
import os
from typing import List, Dict, Any, TypeVar, Type
from . import models

T = TypeVar('T')

class DataManager:
    def __init__(self, data_folder: str = "data"):
        self.data_folder = data_folder
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        self.users_file = os.path.join(data_folder, "users.json")
        self.items_file = os.path.join(data_folder, "items.json")
        self.interactions_file = os.path.join(data_folder, "interactions.json")

    def _read_data(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content: return []
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_data(self, file_path: str, data: List[Dict[str, Any]]):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _load_objects(self, file_path: str, model_class: Type[T]) -> List[T]:
        data = self._read_data(file_path)
        return [model_class(**d) for d in data]

    def _save_objects(self, file_path: str, objects: List[Any]):
        data = [obj.__dict__ for obj in objects]
        self._write_data(file_path, data)

    def get_new_id(self, objects: List[Any]) -> int:
        if not objects:
            return 1
        return max((obj.id for obj in objects), default=0) + 1

    # --- Generic Methods ---
    def get_all(self, model_type: str) -> List[Any]:
        if model_type == 'user': return self._load_objects(self.users_file, models.User)
        if model_type == 'item': return self._load_objects(self.items_file, models.Item)
        if model_type == 'interaction': return self._load_objects(self.interactions_file, models.InterestInteraction)
        raise ValueError(f"Unknown model type: {model_type}")

    def save_all(self, model_type: str, objects: List[Any]):
        if model_type == 'user': self._save_objects(self.users_file, objects)
        elif model_type == 'item': self._save_objects(self.items_file, objects)
        elif model_type == 'interaction': self._save_objects(self.interactions_file, objects)
        else: raise ValueError(f"Unknown model type: {model_type}")