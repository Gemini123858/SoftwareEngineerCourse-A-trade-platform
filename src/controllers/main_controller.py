from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from src.ui_main_window import Ui_MainWindow
from src.services.auth_service import AuthService
from src.services.item_service import ItemService
from src.services.admin_service import AdminService
from src.models import User
from src.controllers.publish_item_controller import PublishItemController
from src.controllers.admin_controller import AdminController

class MainWindowController(QMainWindow):
    def __init__(self, session_id: str, user: User, auth_service: AuthService, item_service: ItemService, admin_service: AdminService):
        super().__init__()
        self.session_id = session_id
        self.user = user
        self.auth_service = auth_service
        self.item_service = item_service
        self.admin_service = admin_service

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.configure_ui_for_user()
        self.setup_connections()
        self.load_all_items()

    def configure_ui_for_user(self):
        """根据用户角色配置UI"""
        self.ui.welcomeLabel.setText(f"Welcome, {self.user.nickname}!")
        if self.user.is_admin:
            self.ui.adminPanelButton.setEnabled(True)
            self.ui.adminPanelButton.setVisible(True)

    def setup_connections(self):
        """连接所有信号和槽"""
        self.ui.searchButton.clicked.connect(self.handle_search)
        self.ui.publishItemButton.clicked.connect(self.open_publish_dialog)
        self.ui.logoutButton.clicked.connect(self.handle_logout)
        self.ui.adminPanelButton.clicked.connect(self.open_admin_panel)
        self.ui.itemTableWidget.itemDoubleClicked.connect(self.show_item_details)

    def handle_search(self):
        keyword = self.ui.searchLineEdit.text()
        items = self.item_service.search_items(keyword)
        self.populate_item_table(items)

    def load_all_items(self):
        """加载并显示所有商品"""
        all_items = self.item_service.get_all_items()
        self.populate_item_table(all_items)

    def populate_item_table(self, items):
        """用商品数据填充表格"""
        self.ui.itemTableWidget.setRowCount(len(items))
        self.ui.itemTableWidget.setHorizontalHeaderLabels(["ID", "Title", "Price", "Status"])
        
        for row, item in enumerate(items):
            self.ui.itemTableWidget.setItem(row, 0, QTableWidgetItem(str(item.id)))
            self.ui.itemTableWidget.setItem(row, 1, QTableWidgetItem(item.title))
            self.ui.itemTableWidget.setItem(row, 2, QTableWidgetItem(f"{item.price:.2f}"))
            self.ui.itemTableWidget.setItem(row, 3, QTableWidgetItem(item.status))
        
        # 让ID列不可编辑
        for row in range(len(items)):
            item_id_cell = self.ui.itemTableWidget.item(row, 0)
            if item_id_cell:
                item_id_cell.setFlags(item_id_cell.flags() & ~Qt.ItemFlag.ItemIsEditable)


    def show_item_details(self, table_item):
        """双击商品时显示详情和联系方式"""
        row = table_item.row()
        item_id = int(self.ui.itemTableWidget.item(row, 0).text())
        
        try:
            contact_info = self.item_service.express_interest(self.session_id, item_id)
            QMessageBox.information(self, "Seller Contact Information", f"Your interest has been recorded. Seller contact information:\n{contact_info}")
        except (ValueError, PermissionError) as e:
            QMessageBox.warning(self, "Operation Failed", str(e))

    def open_publish_dialog(self):
        dialog = PublishItemController(self.session_id, self.item_service)
        if dialog.exec():
            self.load_all_items() # 发布成功后刷新列表

    def open_admin_panel(self):
        dialog = AdminController(self.session_id, self.admin_service)
        dialog.exec()
        self.load_all_items() # 从管理面板返回后刷新

    def handle_logout(self):
        self.auth_service.logout(self.session_id)
        self.close() # 关闭主窗口