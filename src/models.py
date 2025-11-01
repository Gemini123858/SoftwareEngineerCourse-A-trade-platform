"""
定义所有核心业务对象的数据模型。
- 使用 dataclasses 来自动生成 __init__, __repr__ 等方法。
- 使用 time.time() 生成的时间戳（浮点数）代替 Date 对象，因为它更容易被 JSON 序列化。
"""

from dataclasses import dataclass, field
from typing import List
import time

@dataclass
class User:
    id: int
    email: str
    password: str  # 注意：在实际生产项目中，密码绝不能明文存储！
    nickname: str
    contact_info: str
    role: str = "USER"
    created_at: float = field(default_factory=time.time)

@dataclass
class ItemImage:
    id: int
    item_id: int
    image_path: str
    upload_time: float = field(default_factory=time.time)

@dataclass
class Item:
    id: int
    seller_id: int
    title: str
    description: str
    price: float
    status: str = "AVAILABLE"  # 例如: "AVAILABLE", "SOLD"
    # 我们将图片路径直接存在 Item 中，简化模型
    image_paths: List[str] = field(default_factory=list) 
    created_at: float = field(default_factory=time.time)

@dataclass
class InterestInteraction:
    id: int
    item_id: int
    buyer_id: int
    interaction_time: float = field(default_factory=time.time)

# 简化：Admin 的功能暂时不通过特定模型实现，而是通过业务逻辑判断用户角色。