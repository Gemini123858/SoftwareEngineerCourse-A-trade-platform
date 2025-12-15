import pytest
from src.data_manager import DataManager
from src.services.auth_service import AuthService
from src.services.item_service import ItemService
from src.services.admin_service import AdminService

# --- 集成测试环境搭建 ---

@pytest.fixture
def integration_env(tmp_path):
    """
    搭建一个完整的、基于临时文件系统的后端环境。
    所有 Service 共享同一个 DataManager 实例，模拟真实运行时的状态。
    """
    # 使用 pytest 的 tmp_path 创建临时数据目录
    data_dir = tmp_path / "integration_data"
    data_dir.mkdir()
    
    # 初始化底层数据管理器
    dm = DataManager(data_folder=str(data_dir))
    
    # 初始化相互依赖的服务层
    # ItemService 和 AdminService 都依赖 AuthService 进行会话验证
    auth = AuthService(dm)
    item = ItemService(dm, auth)
    admin = AdminService(dm, auth)
    
    return dm, auth, item, admin

# =========================================================
# 集成测试组 1: 完整的 C2C 交易流程 (User Workflow Integration)
# 场景：卖家注册发布 -> 买家注册搜索 -> 买家表示兴趣 -> 验证联系方式交换
# =========================================================

def test_integration_full_trade_cycle(integration_env):
    dm, auth_service, item_service, _ = integration_env
    
    # 1. [AuthService] 卖家注册并登录
    print("\n步骤 1: 卖家注册登录")
    auth_service.register("seller@store.com", "pass1", "SellerBoss", "Phone:10086")
    seller_session, seller_user = auth_service.login("seller@store.com", "pass1")
    
    # 2. [ItemService] 卖家发布商品 (依赖 AuthService 的 Session 解析)
    print("步骤 2: 卖家发布商品")
    # 这里测试了 ItemService 是否能正确通过 session_id 找到刚才 AuthService 创建的用户
    item = item_service.publish_item(seller_session, "Gaming Laptop", "RTX 4090", 20000.0, [])
    assert item.id is not None
    assert item.seller_id == seller_user.id
    
    # 3. [AuthService] 买家注册并登录
    print("步骤 3: 买家注册登录")
    auth_service.register("buyer@home.com", "pass2", "BuyerGuy", "Phone:10010")
    buyer_session, buyer_user = auth_service.login("buyer@home.com", "pass2")
    
    # 4. [ItemService] 买家搜索商品 (测试数据持久化：能否搜到步骤2存入的数据)
    print("步骤 4: 买家搜索商品")
    search_results = item_service.search_items("RTX")
    assert len(search_results) == 1
    target_item = search_results[0]
    assert target_item.id == item.id
    
    # 5. [ItemService] 买家表示兴趣 (测试跨用户数据交互)
    print("步骤 5: 买家表示兴趣")
    # 这里涉及复杂的逻辑：ItemService 需要用 buyer_session 找买家，用 item_id 找商品，再通过商品找卖家
    contact_info = item_service.express_interest(buyer_session, target_item.id)
    
    # 验证结果：买家应该看到了卖家的联系方式
    assert contact_info == "Phone:10086"
    
    # 6. [DataManager] 验证底层数据一致性
    interactions = dm.get_all('interaction')
    assert len(interactions) == 1
    assert interactions[0].buyer_id == buyer_user.id
    assert interactions[0].item_id == target_item.id


# =========================================================
# 集成测试组 2: 管理员监管流程 (Admin Workflow Integration)
# 场景：初始化环境 -> 管理员介入 -> 删除违规商品 -> 封禁违规用户 -> 验证后果
# =========================================================

def test_integration_admin_governance(integration_env):
    dm, auth_service, item_service, admin_service = integration_env
    
    # --- 初始化环境 ---
    # 1. 创建一个普通用户（违规者）
    auth_service.register("spammer@bad.com", "123", "Spammer", "FakeInfo")
    spammer_session, spammer_user = auth_service.login("spammer@bad.com", "123")
    
    # 2. 违规者发布一个非法商品
    bad_item = item_service.publish_item(spammer_session, "Illegal Goods", "Contraband", 999.0, [])
    
    # 3. 创建并手动提升一个管理员 (模拟系统初始化过程)
    # 因为 register 默认是普通用户，我们直接操作底层数据将其提权，这也是集成测试的一种手段
    auth_service.register("admin@sys.com", "adminpass", "Admin", "SysAdmin")
    users = dm.get_all('user')
    for u in users:
        if u.email == "admin@sys.com":
            u.role = "ADMIN"
    dm.save_all('user', users)
    
    # 管理员登录
    admin_session, admin_user = auth_service.login("admin@sys.com", "adminpass")
    assert admin_user.is_admin is True

    # --- 开始测试管理操作 ---

    # 4. [AdminService] 管理员查看所有商品 (测试 AdminService 读取 ItemService 的数据)
    all_items = admin_service.get_all_items(admin_session)
    assert len(all_items) == 1
    assert all_items[0].title == "Illegal Goods"
    
    # 5. [AdminService] 管理员删除违规商品 (测试 AdminService 修改 Item 数据)
    print("\n步骤 5: 管理员删除商品")
    delete_result = admin_service.delete_item(admin_session, bad_item.id)
    assert delete_result is True
    
    # 验证：ItemService 应该再也找不到该商品
    assert len(item_service.get_all_items()) == 0
    assert len(item_service.search_items("Illegal")) == 0
    
    # 6. [AdminService] 管理员封禁用户 (测试 AdminService 修改 User 数据)
    print("步骤 6: 管理员删除用户")
    delete_user_result = admin_service.delete_user(admin_session, spammer_user.id)
    assert delete_user_result is True
    
    # 7. [AuthService] 验证封禁后果 (测试 AuthService 是否响应 AdminService 的修改)
    # 用户尝试再次登录应该失败
    with pytest.raises(ValueError) as excinfo:
        auth_service.login("spammer@bad.com", "123")
    assert "Invalid email" in str(excinfo.value) # 此时邮箱已不存在于系统中
