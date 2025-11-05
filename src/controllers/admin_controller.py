from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from src.ui_admin_dialog import Ui_Dialog as Ui_AdminDialog
from src.services.admin_service import AdminService

class AdminController(QDialog):
    def __init__(self, session_id: str, admin_service: AdminService):
        super().__init__()
        self.session_id = session_id
        self.admin_service = admin_service

        self.ui = Ui_AdminDialog()
        self.ui.setupUi(self)

        self.setup_connections()
        self.load_data()

    def setup_connections(self):
        self.ui.deleteUserButton.clicked.connect(self.delete_selected_user)
        self.ui.deleteItemButton.clicked.connect(self.delete_selected_item)

    def load_data(self):
        """加载所有用户和商品数据到表格中"""
        try:
            # 加载用户
            users = self.admin_service.get_all_users(self.session_id)
            self.ui.userTableWidget.setRowCount(len(users))
            self.ui.userTableWidget.setHorizontalHeaderLabels(["ID", "Nickname", "Email", "Contact", "Role"])
            for row, user in enumerate(users):
                self.ui.userTableWidget.setItem(row, 0, self._create_unediable_item(str(user.id)))
                self.ui.userTableWidget.setItem(row, 1, self._create_unediable_item(user.nickname))
                self.ui.userTableWidget.setItem(row, 2, self._create_unediable_item(user.email))
                self.ui.userTableWidget.setItem(row, 3, self._create_unediable_item(user.contact_info))
                self.ui.userTableWidget.setItem(row, 4, self._create_unediable_item(user.role))

            # 加载商品
            items = self.admin_service.get_all_items(self.session_id)
            self.ui.itemTableWidget.setRowCount(len(items))
            self.ui.itemTableWidget.setHorizontalHeaderLabels(["ID", "Title", "Price", "Seller ID"])
            for row, item in enumerate(items):
                self.ui.itemTableWidget.setItem(row, 0, self._create_unediable_item(str(item.id)))
                self.ui.itemTableWidget.setItem(row, 1, self._create_unediable_item(item.title))
                self.ui.itemTableWidget.setItem(row, 2, self._create_unediable_item(f"{item.price:.2f}"))
                self.ui.itemTableWidget.setItem(row, 3, self._create_unediable_item(str(item.seller_id)))

        except PermissionError as e:
            self.ui.errorLabel.setText(str(e))

    def delete_selected_user(self):
        selected_rows = self.ui.userTableWidget.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Operation Failed", "Please select a user to delete.")
            return

        user_id = int(self.ui.userTableWidget.item(selected_rows[0].row(), 0).text())

        reply = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete the user with ID {user_id}? This action cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.admin_service.delete_user(self.session_id, user_id)
                self.load_data() # 刷新
            except (ValueError, PermissionError) as e:
                QMessageBox.critical(self, "Deletion Failed", str(e))

    def delete_selected_item(self):
        selected_rows = self.ui.itemTableWidget.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Operation Failed", "Please select an item to delete.")
            return
        
        item_id = int(self.ui.itemTableWidget.item(selected_rows[0].row(), 0).text())

        reply = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete the item with ID {item_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.admin_service.delete_item(self.session_id, item_id)
                self.load_data() # 刷新
            except (ValueError, PermissionError) as e:
                QMessageBox.critical(self, "Deletion Failed", str(e))

    def _create_unediable_item(self, text: str) -> QTableWidgetItem:
        """创建一个不可编辑的表格项"""
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item