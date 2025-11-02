from PyQt5.QtWidgets import QDialog
from src.ui_login_window import Ui_LoginDialog
from src.services.auth_service import AuthService
from src.controllers.register_controller import RegisterController
class LoginController(QDialog):
    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.session_id = None
        self.user = None

        self.ui = Ui_LoginDialog()
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
        # 隐藏登录窗口，打开注册窗口
        self.hide()
        register_dialog = RegisterController(self.auth_service)
        register_dialog.exec()
        # 无论注册成功与否，都重新显示登录窗口
        self.show()