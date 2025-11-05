from PyQt5.QtWidgets import QDialog
from src.ui_publish_item_dialog import Ui_PublishItem
from src.services.item_service import ItemService

class PublishItemController(QDialog):
    def __init__(self, session_id: str, item_service: ItemService):
        super().__init__()
        self.session_id = session_id
        self.item_service = item_service

        self.ui = Ui_PublishItem()
        self.ui.setupUi(self)

        self.ui.submitButton.clicked.connect(self.handle_submit)

    def handle_submit(self):
        title = self.ui.titleLineEdit.text().strip()
        description = self.ui.descriptionTextEdit.toPlainText().strip()
        price = self.ui.priceDoubleSpinBox.value()

        if not title or not description:
            self.ui.errorLabel.setText("Title and description cannot be empty.")
            return
        
        try:
            # 图片路径暂时留空
            self.item_service.publish_item(self.session_id, title, description, price, [])
            self.accept() # 成功后关闭对话框
        except PermissionError as e:
            self.ui.errorLabel.setText(f"Publishing Failed: {e}")