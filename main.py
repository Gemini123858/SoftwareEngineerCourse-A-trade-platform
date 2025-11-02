import sys
from PyQt5.QtWidgets import QApplication
from src.data_manager import DataManager
from src.services.auth_service import AuthService
from src.services.item_service import ItemService
from src.services.admin_service import AdminService
from src.controllers.login_controller import LoginController
from src.controllers.main_controller import MainWindowController
import os

def setup_initial_data(data_manager: DataManager, auth_service: AuthService):
    """如果用户数据为空，则创建一个管理员账户"""
    users = data_manager.get_all('user')
    if not users:
        print("No users found. Creating initial admin user...")
        admin_user = auth_service.register("admin@app.com", "admin123", "Admin", "Internal")
        admin_user.role = "ADMIN"
        # 需要重新获取并保存，因为register已经保存过一次
        all_users = data_manager.get_all('user')
        for i, u in enumerate(all_users):
            if u.id == admin_user.id:
                all_users[i] = admin_user
                break
        data_manager.save_all('user', all_users)
        print("--- Initial setup complete. Admin user created. ---")

def main():
    # --- 1. 初始化应用和所有服务 ---
    app = QApplication(sys.argv)
    
    data_manager = DataManager(data_folder="data")
    auth_service = AuthService(data_manager)
    item_service = ItemService(data_manager, auth_service)
    admin_service = AdminService(data_manager, auth_service)

    # 确保至少有一个管理员账户存在
    setup_initial_data(data_manager, auth_service)

    # --- 2. 启动应用主循环 ---
    while True:
        # 显示登录窗口
        login_dialog = LoginController(auth_service)
        
        # 如果登录成功 (dialog.exec() 返回 1)
        if login_dialog.exec():
            # 获取登录信息
            session_id = login_dialog.session_id
            user = login_dialog.user
            
            # 创建并显示主窗口
            main_window = MainWindowController(session_id, user, auth_service, item_service, admin_service)
            main_window.show()
            
            # app.exec() 会阻塞，直到主窗口关闭
            app.exec()
            
            # 主窗口关闭后 (用户登出), 循环会继续，再次显示登录窗口
            print("User logged out. Returning to login screen.")
        else:
            # 如果用户关闭了登录窗口，则退出整个应用
            print("Login cancelled. Exiting application.")
            break # 退出循环

if __name__ == "__main__":
    main()