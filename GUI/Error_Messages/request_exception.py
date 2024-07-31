from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPushButton

from PySide6.QtCore import Qt

from scripts.tags import OrthancRequestError
class RequestExceptionDialog(QDialog):
    
    def __init__(self, error : OrthancRequestError, parent=None):
        super().__init__(parent)
        self.v_layout = QVBoxLayout()
        
        self.error : OrthancRequestError = error
        
        self.description = QLabel("The following error has been raised : ", self)
        self.v_layout.addWidget(self.description)
        
        detail_text = QLabel(f"{self.error}")
        self.v_layout.addWidget(detail_text)

        self.explication = QLabel("Do you want to proceed with the dicomization process of other studies ?", self)
        self.v_layout.addWidget(self.explication)
        
        self.buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)
        self.buttonBox.addButton(QPushButton("Continue"), QDialogButtonBox.ButtonRole.AcceptRole)
        self.buttonBox.addButton(QPushButton("Cancel All"), QDialogButtonBox.ButtonRole.RejectRole)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        
        
        self.v_layout.addWidget(self.buttonBox)
        
        self.setLayout(self.v_layout)
        
        self.adjustSize()
        
        