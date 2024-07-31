from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPushButton

from PySide6.QtCore import Qt

class NotAllCorrectDialog(QDialog):
    
    def __init__(self, list_studies : list[str], parent=None):
        super().__init__(parent)
        self.v_layout = QVBoxLayout()
        
        self.list_studies = list_studies
        
        self.description = QLabel("These studies are not complete in the tag json : ", self)
        self.v_layout.addWidget(self.description)
        
        for study in self.list_studies:
            value_text = QLabel(f"- {study}")
            self.v_layout.addWidget(value_text)
        
        self.explication = QLabel("Do you want to proceed without them ?", self)
        self.v_layout.addWidget(self.explication)
        
        self.buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)
        self.buttonBox.addButton(QPushButton("Continue"), QDialogButtonBox.ButtonRole.AcceptRole)
        self.buttonBox.addButton(QPushButton("Cancel All"), QDialogButtonBox.ButtonRole.RejectRole)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        
        
        self.v_layout.addWidget(self.buttonBox)
        
        self.setLayout(self.v_layout)
        
        self.adjustSize()