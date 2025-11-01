"""
负责商品相关的业务逻辑，如发布、搜索和用户交互。
"""
from typing import List
from src.data_manager import DataManager
from src.models import Item, InterestInteraction
from src.services.auth_service import AuthService

class ItemService:
    def __init__(self, data_manager: DataManager, auth_service: AuthService):
        self.data_manager = data_manager
        self.auth_service = auth_service

    def publish_item(self, session_id: str, title: str, description: str, price: float, image_paths: List[str]) -> Item:
        seller = self.auth_service.get_user_from_session(session_id)
        if not seller:
            raise PermissionError("Invalid session. Please log in.")

        items = self.data_manager.get_all('item')
        new_id = self.data_manager.get_new_id(items)
        new_item = Item(
            id=new_id,
            seller_id=seller.id,
            title=title,
            description=description,
            price=price,
            image_paths=image_paths
        )
        items.append(new_item)
        self.data_manager.save_all('item', items)
        return new_item

    def get_all_items(self) -> List[Item]:
        return self.data_manager.get_all('item')

    def search_items(self, keyword: str) -> List[Item]:
        keyword = keyword.lower().strip()
        all_items = self.get_all_items()
        if not keyword:
            return all_items
        
        return [
            item for item in all_items
            if keyword in item.title.lower() or keyword in item.description.lower()
        ]

    def express_interest(self, session_id: str, item_id: int) -> str:
        buyer = self.auth_service.get_user_from_session(session_id)
        if not buyer:
            raise PermissionError("Invalid session. Please log in.")

        items = self.data_manager.get_all('item')
        item = next((i for i in items if i.id == item_id), None)
        if not item:
            raise ValueError("Item not found.")

        if item.seller_id == buyer.id:
            raise ValueError("You cannot express interest in your own item.")

        interactions = self.data_manager.get_all('interaction')
        new_id = self.data_manager.get_new_id(interactions)
        interaction = InterestInteraction(id=new_id, item_id=item_id, buyer_id=buyer.id)
        interactions.append(interaction)
        self.data_manager.save_all('interaction', interactions)

        users = self.data_manager.get_all('user')
        seller = next((u for u in users if u.id == item.seller_id), None)
        if not seller:
            # This case should ideally not happen if data is consistent
            raise ValueError("Seller not found for this item.")
            
        return seller.contact_info
