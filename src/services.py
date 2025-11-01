"""
服务层，包含所有核心业务逻辑。
它处理来自 UI 的请求，并使用 DataManager 来操作数据。
"""

from .data_manager import DataManager
from .models import User, Item, InterestInteraction
from typing import List

class AuthService:
    """处理用户认证相关的所有逻辑"""
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.current_user: User | None = None

    def register(self, email: str, password: str, nickname: str, contact_info: str) -> User | None:
        """注册新用户"""
        if self.data_manager.get_user_by_email(email):
            print(f"注册失败：邮箱 {email} 已被占用。")
            return None
        
        new_id = self.data_manager.get_new_user_id()
        # 简化处理：密码应该被哈希加密
        new_user = User(
            id=new_id, 
            email=email, 
            password=password, 
            nickname=nickname, 
            contact_info=contact_info
        )
        self.data_manager.save_user(new_user)
        print(f"用户 {nickname} 注册成功！")
        return new_user

    def login(self, email: str, password: str) -> bool:
        """用户登录"""
        user = self.data_manager.get_user_by_email(email)
        # 简化处理：密码应该是比对哈希值
        if user and user.password == password:
            self.current_user = user
            print(f"登录成功，欢迎 {user.nickname}！")
            return True
        
        self.current_user = None
        print("登录失败：邮箱或密码错误。")
        return False

    def logout(self):
        """用户登出"""
        print(f"用户 {self.current_user.nickname} 已登出。")
        self.current_user = None


class ItemService:
    """处理商品和交互相关的所有逻辑"""
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def publish_item(self, seller: User, title: str, description: str, price: float, image_paths: List[str]) -> Item:
        """发布一个新商品"""
        new_id = self.data_manager.get_new_item_id()
        new_item = Item(
            id=new_id,
            seller_id=seller.id,
            title=title,
            description=description,
            price=price,
            image_paths=image_paths
        )
        self.data_manager.save_item(new_item)
        print(f"用户 {seller.nickname} 成功发布商品：'{title}'。")
        return new_item

    def search_items(self, keyword: str) -> List[Item]:
        """根据关键词搜索商品"""
        keyword = keyword.lower()
        all_items = self.data_manager.get_all_items()
        
        if not keyword:
            return all_items # 如果关键词为空，返回所有商品

        results = [
            item for item in all_items 
            if keyword in item.title.lower() or keyword in item.description.lower()
        ]
        return results

    def express_interest(self, item: Item, buyer: User) -> str | None:
        """
        买家对商品表示兴趣。
        记录交互，并返回卖家的联系方式。
        """
        if item.seller_id == buyer.id:
            print("你不能对自己的商品表示兴趣。")
            return None

        # 1. 获取卖家信息
        seller = self.data_manager.get_user_by_id(item.seller_id)
        if not seller:
            print("错误：找不到该商品的卖家。")
            return None

        # 2. 创建并保存交互记录
        new_interaction_id = self.data_manager.get_new_interaction_id()
        interaction = InterestInteraction(
            id=new_interaction_id,
            item_id=item.id,
            buyer_id=buyer.id
        )
        self.data_manager.save_interaction(interaction)
        print(f"用户 {buyer.nickname} 对商品 '{item.title}' 表示了兴趣。")

        # 3. 返回卖家联系方式
        return seller.contact_info
