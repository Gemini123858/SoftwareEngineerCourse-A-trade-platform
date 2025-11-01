"""
定义所有核心业务对象的数据模型。
"""

from dataclasses import dataclass, field
import time
from typing import List

@dataclass
class User:
    id: int
    email: str
    password_hash: str  # 已重命名，强调密码不应明文存储
    nickname: str
    contact_info: str
    role: str = "USER"  # 'USER' 或 'ADMIN'
    created_at: float = field(default_factory=time.time)

    @property
    def is_admin(self) -> bool:
        return self.role == "ADMIN"

@dataclass
class Item:
    id: int
    seller_id: int
    title: str
    description: str
    price: float
    status: str = "AVAILABLE"
    image_paths: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

@dataclass
class InterestInteraction:
    id: int
    item_id: int
    buyer_id: int
    interaction_time: float = field(default_factory=time.time)