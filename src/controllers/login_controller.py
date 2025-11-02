from PyQt5.QtWidgets import QDialog
from src.ui_login_window import Ui_login_window
from src.services.auth_service import AuthService
from src.controllers.register_controller import RegisterController


REOPEN_CODE = 101 # 一个自定义的、不会与PyQt内置代码冲突的数字

class LoginController(QDialog):
    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.session_id = None
        self.user = None

        self.ui = Ui_login_window()
        self.ui.setupUi(self)

        # 连接信号与槽
        self.ui.loginButton.clicked.connect(self.handle_login)
        self.ui.goToRegisterButton.clicked.connect(self.open_register_dialog)

    def handle_login(self):
        email = self.ui.emailLineEdit.text().strip()
        password = self.ui.passwordLineEdit.text()

        if not email or not password:
            self.ui.errorLabel.setText("邮箱和密码不能为空。")
            return

        try:
            self.session_id, self.user = self.auth_service.login(email, password)
            self.accept()  # 登录成功，关闭对话框
        except ValueError as e:
            self.ui.errorLabel.setText(f"登录失败: {e}")

    def open_register_dialog(self):
        register_dialog = RegisterController(self.auth_service)
        
        # register_dialog.exec() 会在注册成功时返回 Accepted
        if register_dialog.exec():
            # 如果注册成功，我们用自定义代码关闭当前的登录窗口
            # 这样主循环就知道要重新打开一个新的登录窗口了
            self.done(REOPEN_CODE)
        # 如果用户只是关闭了注册窗口（没有注册成功），则什么也不做
        # 当前的登录窗口会保持打开状态