import pytest
from unittest.mock import MagicMock
from src.services.auth_service import AuthService
from src.services.item_service import ItemService
from src.models import User, Item
from src.data_manager import DataManager

# --- Fixtures: 初始化测试环境 ---

@pytest.fixture
def mock_data_manager():
    """创建一个模拟的数据管理器，避免读写真实文件"""
    dm = MagicMock(spec=DataManager)
    # 模拟 get_new_id 方法，简单的自增逻辑
    def side_effect_get_id(objects):
        if not objects: return 1
        return max(obj.id for obj in objects) + 1
    dm.get_new_id.side_effect = side_effect_get_id
    
    # 模拟数据存储列表
    dm.users = []
    dm.items = []
    dm.interactions = []
    
    # 模拟 get_all 方法
    def side_effect_get_all(model_type):
        if model_type == 'user': return dm.users
        if model_type == 'item': return dm.items
        if model_type == 'interaction': return dm.interactions
        return []
    dm.get_all.side_effect = side_effect_get_all
    
    return dm

@pytest.fixture
def auth_service(mock_data_manager):
    return AuthService(mock_data_manager)

@pytest.fixture
def item_service(mock_data_manager, auth_service):
    return ItemService(mock_data_manager, auth_service)

# --- Test Suite 1: AuthService (认证服务测试) ---

class TestAuthService:
    
    # 1. 注册成功 (基本路径)
    def test_register_success(self, auth_service, mock_data_manager):
        user = auth_service.register("test@test.com", "123456", "TestUser", "Phone:123")
        
        assert user.email == "test@test.com"
        assert user.nickname == "TestUser"
        assert len(mock_data_manager.users) == 1
        assert mock_data_manager.save_all.called

    # 2. 注册重复邮箱 (边界/错误处理)
    def test_register_duplicate_email(self, auth_service, mock_data_manager):
        # 先注册一个
        mock_data_manager.users.append(User(1, "dup@test.com", "hash", "U1", "C1"))
        
        with pytest.raises(ValueError, match="already registered"):
            auth_service.register("dup@test.com", "654321", "User2", "C2")

    # 3. 密码哈希模拟检查 (数据验证)
    def test_register_password_hashing(self, auth_service):
        user = auth_service.register("hash@test.com", "mypwd", "Hasher", "C1")
        # 验证代码中模拟的 "hashed_" 前缀逻辑
        assert user.password_hash == "hashed_mypwd"
        assert user.password_hash != "mypwd"

    # 4. 默认角色检查 (默认值验证)
    def test_register_default_role(self, auth_service):
        user = auth_service.register("role@test.com", "pwd", "RoleUser", "C1")
        assert user.role == "USER"
        assert user.is_admin is False

    # 5. 登录成功 (基本路径)
    def test_login_success(self, auth_service, mock_data_manager):
        user = User(1, "login@test.com", "hashed_123", "LoginUser", "C1")
        mock_data_manager.users.append(user)
        
        session_id, logged_in_user = auth_service.login("login@test.com", "123")
        assert session_id is not None
        assert logged_in_user == user

    # 6. 登录失败 - 密码错误 (错误处理)
    def test_login_wrong_password(self, auth_service, mock_data_manager):
        user = User(1, "wrong@test.com", "hashed_correct", "User", "C1")
        mock_data_manager.users.append(user)
        
        with pytest.raises(ValueError, match="Invalid email or password"):
            auth_service.login("wrong@test.com", "wrong_pwd")

    # 7. 登录失败 - 邮箱不存在 (错误处理)
    def test_login_email_not_found(self, auth_service):
        with pytest.raises(ValueError, match="Invalid email or password"):
            auth_service.login("ghost@test.com", "123")

    # 8. 通过会话获取用户 - 成功 (状态管理)
    def test_get_user_from_session_valid(self, auth_service, mock_data_manager):
        user = User(99, "session@test.com", "hashed_pwd", "SessionUser", "C1")
        mock_data_manager.users.append(user)
        
        session_id, _ = auth_service.login("session@test.com", "pwd") # 这会在内部 _SESSIONS 注册
        retrieved_user = auth_service.get_user_from_session(session_id)
        assert retrieved_user.id == 99

    # 9. 通过会话获取用户 - 无效会话 (边界条件)
    def test_get_user_from_session_invalid(self, auth_service):
        user = auth_service.get_user_from_session("fake-uuid-1234")
        assert user is None

    # 10. 登出功能 (状态转换)
    def test_logout(self, auth_service, mock_data_manager):
        user = User(1, "out@test.com", "hashed_pwd", "U", "C")
        mock_data_manager.users.append(user)
        session_id, _ = auth_service.login("out@test.com", "pwd")
        
        # 确保登录状态有效
        assert auth_service.get_user_from_session(session_id) is not None
        
        # 登出
        auth_service.logout(session_id)
        
        # 再次获取应为空
        assert auth_service.get_user_from_session(session_id) is None


# --- Test Suite 2: ItemService (商品服务测试) ---

class TestItemService:
    
    @pytest.fixture
    def seller_session(self, auth_service, mock_data_manager):
        """Helper: 创建一个卖家并登录，返回session_id"""
        user = User(10, "seller@test.com", "hashed_123", "Seller", "SellerContact")
        mock_data_manager.users.append(user)
        session_id, _ = auth_service.login("seller@test.com", "123")
        return session_id

    # 1. 发布商品 - 成功 (基本路径)
    def test_publish_item_success(self, item_service, mock_data_manager, seller_session):
        item = item_service.publish_item(seller_session, "Gaming PC", "High end", 2000.0, [])
        
        assert item.title == "Gaming PC"
        assert item.seller_id == 10
        assert len(mock_data_manager.items) == 1
        assert mock_data_manager.save_all.called

    # 2. 发布商品 - 未登录 (权限控制)
    def test_publish_item_no_session(self, item_service):
        with pytest.raises(PermissionError, match="Invalid session"):
            item_service.publish_item("invalid-session", "Title", "Desc", 100.0, [])

    # 3. 搜索商品 - 精确匹配 (查询逻辑)
    def test_search_items_exact(self, item_service, mock_data_manager):
        mock_data_manager.items = [
            Item(1, 1, "Apple iPhone", "Phone", 500.0),
            Item(2, 1, "Samsung Galaxy", "Phone", 400.0)
        ]
        results = item_service.search_items("iPhone")
        assert len(results) == 1
        assert results[0].title == "Apple iPhone"

    # 4. 搜索商品 - 描述匹配 (查询逻辑)
    def test_search_items_by_description(self, item_service, mock_data_manager):
        mock_data_manager.items = [
            Item(1, 1, "Laptop", "Gaming device", 1000.0),
            Item(2, 1, "Mouse", "Office device", 20.0)
        ]
        results = item_service.search_items("Gaming")
        assert len(results) == 1
        assert results[0].id == 1

    # 5. 搜索商品 - 忽略大小写 (用户体验/边界)
    def test_search_items_case_insensitive(self, item_service, mock_data_manager):
        mock_data_manager.items = [Item(1, 1, "Big KEYBOARD", "desc", 10.0)]
        results = item_service.search_items("keyboard") # 小写搜大写
        assert len(results) == 1

    # 6. 搜索商品 - 空关键词返回所有 (边界条件)
    def test_search_items_empty_keyword(self, item_service, mock_data_manager):
        mock_data_manager.items = [Item(1, 1, "A", "a", 1), Item(2, 1, "B", "b", 1)]
        results = item_service.search_items("")
        assert len(results) == 2

    # 7. 搜索商品 - 无结果 (边界条件)
    def test_search_items_no_results(self, item_service, mock_data_manager):
        mock_data_manager.items = [Item(1, 1, "Car", "Vehicle", 10000.0)]
        results = item_service.search_items("Airplane")
        assert len(results) == 0

    # 8. 表示兴趣 - 成功 (业务逻辑)
    def test_express_interest_success(self, item_service, mock_data_manager, auth_service):
        # 准备卖家
        seller = User(10, "s@s.com", "hashed_p", "Seller", "WX:Seller")
        mock_data_manager.users.append(seller)
        # 准备商品
        item = Item(100, 10, "Book", "Old book", 10.0)
        mock_data_manager.items.append(item)
        
        # 准备买家登录
        buyer = User(20, "b@b.com", "hashed_b", "Buyer", "WX:Buyer")
        mock_data_manager.users.append(buyer)
        buyer_session, _ = auth_service.login("b@b.com", "b") 

        # 执行
        contact = item_service.express_interest(buyer_session, 100)
        
        assert contact == "WX:Seller"
        assert len(mock_data_manager.interactions) == 1
        assert mock_data_manager.interactions[0].buyer_id == 20
        assert mock_data_manager.interactions[0].item_id == 100

    # 9. 表示兴趣 - 无法对自己的商品感兴趣 (业务规则/边界)
    def test_express_interest_own_item(self, item_service, mock_data_manager, seller_session):
        # 卖家发布了一个商品
        mock_data_manager.items.append(Item(50, 10, "My Item", "desc", 50.0)) # ID 10 is seller in fixture
        
        with pytest.raises(ValueError, match="cannot express interest in your own item"):
            item_service.express_interest(seller_session, 50)

    # 10. 表示兴趣 - 商品不存在 (错误处理)
    def test_express_interest_item_not_found(self, item_service, mock_data_manager, seller_session):
        with pytest.raises(ValueError, match="Item not found"):
            item_service.express_interest(seller_session, 9999)

    # 11. 表示兴趣 - 未登录 (权限控制)
    def test_express_interest_no_session(self, item_service):
        with pytest.raises(PermissionError):
            item_service.express_interest("fake-session", 1)
