"""
项目主入口文件和后端功能演示。
"""
from src.data_manager import DataManager
from src.services.auth_service import AuthService
from src.services.item_service import ItemService
from src.services.admin_service import AdminService
import os

# ... (后续代码与上一版完全相同) ...
def setup_initial_data(data_manager: DataManager, auth_service: AuthService):
    """清空数据并创建一个管理员账户"""
    for file in [data_manager.users_file, data_manager.items_file, data_manager.interactions_file]:
        if os.path.exists(file):
            os.remove(file)
    
    # 创建管理员
    users = data_manager.get_all('user')
    admin_user = auth_service.register("admin@app.com", "admin123", "Admin", "Internal")
    admin_user.role = "ADMIN"
    users = [u if u.id != admin_user.id else admin_user for u in data_manager.get_all('user')]
    data_manager.save_all('user', users)
    print("--- Initial setup complete. Admin user created. ---")


def run_demo():
    # --- 1. 初始化所有服务 ---
    data_manager = DataManager(data_folder="data")
    auth_service = AuthService(data_manager)
    item_service = ItemService(data_manager, auth_service)
    admin_service = AdminService(data_manager, auth_service)
    
    setup_initial_data(data_manager, auth_service)

    # --- 2. 模拟用户注册和登录 ---
    print("\n--- 模拟用户注册与登录 ---")
    try:
        auth_service.register("zhangsan@a.com", "pass123", "张三", "wx:zhangsan")
        zhangsan_session, _ = auth_service.login("zhangsan@a.com", "pass123")
        print(f"张三登录成功，会话ID: ...{zhangsan_session[-6:]}")

        auth_service.register("lisi@b.com", "pass456", "李四", "qq:12345")
        lisi_session, _ = auth_service.login("lisi@b.com", "pass456")
        print(f"李四登录成功，会话ID: ...{lisi_session[-6:]}")
    except ValueError as e:
        print(f"发生错误: {e}")

    # --- 3. 模拟不同用户发布商品 ---
    print("\n--- 模拟发布商品 ---")
    try:
        item_service.publish_item(zhangsan_session, "九成新键盘", "机械键盘，手感好", 150.0, [])
        print("张三发布了键盘。")
        item_service.publish_item(lisi_session, "二手显示器", "24寸 1080p", 400.0, [])
        print("李四发布了显示器。")
    except PermissionError as e:
        print(f"发生错误: {e}")
        
    # --- 4. 模拟搜索和表示兴趣 ---
    print("\n--- 模拟搜索与交互 ---")
    keyboard = item_service.search_items("键盘")[0]
    print(f"搜索到商品: {keyboard.title}")
    try:
        # 李四对张三的键盘感兴趣
        contact = item_service.express_interest(lisi_session, keyboard.id)
        print(f"李四成功获取到张三的联系方式: {contact}")
    except (ValueError, PermissionError) as e:
        print(f"发生错误: {e}")

    # --- 5. 模拟管理员操作 ---
    print("\n--- 模拟管理员登录与操作 ---")
    try:
        admin_session, _ = auth_service.login("admin@app.com", "admin123")
        print("管理员登录成功。")
        
        all_users = admin_service.get_all_users(admin_session)
        print(f"管理员获取到系统所有用户: {[u.nickname for u in all_users]}")
        
        # 管理员删除李四发布的显示器
        monitor = item_service.search_items("显示器")[0]
        admin_service.delete_item(admin_session, monitor.id)
        print(f"管理员删除了商品: '{monitor.title}'")
        
        # 验证商品是否已被删除
        remaining_items = item_service.get_all_items()
        print(f"系统中剩余商品: {[i.title for i in remaining_items]}")

    except (ValueError, PermissionError) as e:
        print(f"管理员操作失败: {e}")

    # --- 6. 模拟权限错误 ---
    print("\n--- 模拟权限错误 ---")
    try:
        # 普通用户张三尝试删除商品
        print("张三（普通用户）尝试删除键盘...")
        admin_service.delete_item(zhangsan_session, keyboard.id)
    except PermissionError as e:
        print(f"操作失败，正如预期: {e}")


if __name__ == "__main__":
    run_demo()