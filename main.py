import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from src.data_manager import DataManager
from src.services.auth_service import AuthService
from src.services.item_service import ItemService
from src.services.admin_service import AdminService
from src.controllers.login_controller import LoginController
from src.controllers.main_controller import MainWindowController
import os
from src.controllers.login_controller import REOPEN_CODE

# export QT_QPA_PLATFORM_PLUGIN_PATH=/mnt/e/软件工程/Exp3/venv/lib/python3.10/site-packages/PyQt5/Qt5/plugins/platforms
# before running the application, especially on Linux.

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
        login_dialog = LoginController(auth_service)
        result = login_dialog.exec() # 获取返回码

        if result == QDialog.DialogCode.Accepted: # 登录成功
            session_id = login_dialog.session_id
            user = login_dialog.user
            
            main_window = MainWindowController(session_id, user, auth_service, item_service, admin_service)
            main_window.show()
            
            app.exec() # 等待主窗口关闭 (登出)
            # 主窗口关闭后，循环继续，会重新显示登录窗口
            print("User logged out. Returning to login screen.")
            continue # 明确地继续下一次循环

        elif result == REOPEN_CODE: # 注册成功，需要重新打开登录窗口
            print("Registration successful. Re-opening login screen.")
            continue # 直接进入下一次循环，创建新的 LoginController

        else: # 用户关闭了登录窗口或以其他方式取消
            print("Login cancelled. Exiting application.")
            break # 退出循环

if __name__ == "__main__":
    main()