"""
项目主入口文件。
目前用于演示后端服务的功能。
未来将用于初始化和启动 PyQt GUI 应用。
"""

from src.data_manager import DataManager
from src.services import AuthService, ItemService

def run_backend_demo():
    print("--- 启动二手交易平台后端演示 ---")
    
    # 1. 初始化核心服务
    # 我们将数据存储在项目根目录下的 'data' 文件夹中
    data_manager = DataManager(data_folder="../data")
    auth_service = AuthService(data_manager)
    item_service = ItemService(data_manager)
    
    # 2. 模拟用户注册
    print("\n--- 步骤1: 用户注册 ---")
    user_zhangsan = auth_service.register("zhangsan@example.com", "pass123", "张三", "wx:zhangsan123")
    user_lisi = auth_service.register("lisi@example.com", "pass456", "李四", "QQ:123456789")
    auth_service.register("lisi@example.com", "pass789", "李四重复", "QQ:987654321") # 演示注册失败
    
    if not user_zhangsan or not user_lisi:
        print("演示因注册失败而终止。")
        return

    # 3. 模拟用户登录
    print("\n--- 步骤2: 用户登录 ---")
    auth_service.login("zhangsan@example.com", "pass123")
    
    # 4. 模拟发布商品
    print("\n--- 步骤3: 发布商品 ---")
    if auth_service.current_user:
        item_service.publish_item(
            seller=auth_service.current_user,
            title="智能手机",
            description="几乎全新，配件齐全",
            price=1800.00,
            image_paths=["/images/phone.jpg"]
        )
    
    auth_service.logout() # 张三登出
    auth_service.login("lisi@example.com", "pass456") # 李四登录
    
    if auth_service.current_user:
        item_service.publish_item(
            seller=auth_service.current_user,
            title="二手笔记本电脑",
            description="九成新，配置良好",
            price=2500.00,
            image_paths=["/images/laptop.jpg"]
        )

    # 5. 模拟搜索商品
    print("\n--- 步骤4: 搜索商品 ---")
    search_results = item_service.search_items("电脑")
    print(f"搜索 '电脑' 找到 {len(search_results)} 个结果:")
    for item in search_results:
        print(f"  - ID: {item.id}, 标题: {item.title}, 价格: {item.price}")
        
    # 6. 模拟用户表示兴趣
    print("\n--- 步骤5: 用户表示兴趣 ---")
    auth_service.logout() # 李四登出
    auth_service.login("zhangsan@example.com", "pass123") # 张三登录
    
    laptop = item_service.search_items("笔记本")[0]
    if laptop and auth_service.current_user:
        contact = item_service.express_interest(laptop, auth_service.current_user)
        if contact:
            print(f"成功获取卖家联系方式: {contact}")

    print("\n--- 后端演示结束 ---")


if __name__ == "__main__":
    run_backend_demo()