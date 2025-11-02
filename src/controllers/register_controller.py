from PyQt5.QtWidgets import QDialog, QMessageBox
from src.ui_register_dialog import Ui_RegisterDialog
from src.services.auth_service import AuthService

class RegisterController(QDialog):
    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        
        self.ui = Ui_RegisterDialog()
        self.ui.setupUi(self)

        self.ui.registerButton.clicked.connect(self.handle_register)

    def handle_register(self):
        email = self.ui.emailLineEdit.text().strip()
        password = self.ui.passwordLineEdit.text()
        confirm_password = self.ui.confirmPasswordLineEdit.text()
        nickname = self.ui.nicknameLineEdit.text().strip()
        contact_info = self.ui.contactInfoLineEdit.text().strip()

        # 输入验证
        if not all([email, password, confirm_password, nickname, contact_info]):
            self.ui.errorLabel.setText("所有字段均为必填项。")
            return
        if password != confirm_password:
            self.ui.errorLabel.setText("两次输入的密码不一致。")
            return

        try:
            self.auth_service.register(email, password, nickname, contact_info)
            # 弹窗提示成功
            QMessageBox.information(self, "注册成功", "您的账户已成功创建！现在可以返回登录了。")
            self.accept() # 关闭注册窗口
        except ValueError as e:
            self.ui.errorLabel.setText(f"注册失败: {e}")