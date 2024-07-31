from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPushButton

from PySide6.QtCore import Qt
class WrongValue:
    
    def __init__(self, tag_name, module_value, new_value):
        self.tag_name = tag_name
        self.module_value = module_value
        self.new_value = new_value

class WrongValueDialog(QDialog):
    
    def __init__(self, list_values : list[WrongValue], parent=None):
        super().__init__(parent)
        self.v_layout = QVBoxLayout()
        
        self.list_values = list_values
        
        self.description = QLabel("These values are not consistent with their parent modules : ", self)
        self.v_layout.addWidget(self.description)
        
        for wrong_value in self.list_values:
            value_text = QLabel(f"- {wrong_value.tag_name} : {wrong_value.new_value} =/= {wrong_value.module_value}")
            self.v_layout.addWidget(value_text)
        
        self.explication = QLabel("Do you want to proceed with the module value ?", self)
        self.v_layout.addWidget(self.explication)
        
        self.buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)
        self.buttonBox.addButton(QPushButton("Continue"), QDialogButtonBox.ButtonRole.AcceptRole)
        self.buttonBox.addButton(QPushButton("Cancel All"), QDialogButtonBox.ButtonRole.RejectRole)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        
        
        self.v_layout.addWidget(self.buttonBox)
        
        self.setLayout(self.v_layout)
        
        self.adjustSize()
        
        