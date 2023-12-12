# Sphaeroptica - 3D Viewer on calibrated

# Copyright (C) 2023 Yann Pollet, Royal Belgian Institute of Natural Sciences

#

# This program is free software: you can redistribute it and/or

# modify it under the terms of the GNU General Public License as

# published by the Free Software Foundation, either version 3 of the

# License, or (at your option) any later version.

# 

# This program is distributed in the hope that it will be useful, but

# WITHOUT ANY WARRANTY; without even the implied warranty of

# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU

# General Public License for more details.

#

# You should have received a copy of the GNU General Public License

# along with this program. If not, see <http://www.gnu.org/licenses/>.


import sys
# setting path
sys.path.append('.')

from PySide6.QtWidgets import (
    QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QCheckBox, QLabel, QLineEdit, QPushButton
)
from PySide6.QtGui import (
    QAction, QIcon
)
from PySide6.QtCore import (
    Qt
)

class _DicomWidget(QWidget):
    """_Widget asking for the DICOM files that needs to have tags
    """

    def __init__(self,parent=None):
        super(_DicomWidget, self).__init__(parent)
        self.parent = parent
        # Choice of Directory
        get_dir = QHBoxLayout()
        label = QLabel("Dicom Files : ")
        get_dir.addWidget(label)
        
        self.cal_dir_edit=QLabel("No files selected") 
        get_dir.addWidget(self.cal_dir_edit)
        
        cam_calib = QPushButton(text="Browse...",parent=self)
        cam_calib.clicked.connect(self.open_directory)

        get_dir.addWidget(cam_calib)
        get_dir.setSpacing(20)
        self.setLayout(get_dir)
        
        get_dir.setContentsMargins(20,0,100,0)

    def open_directory(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select DICOM files", ".", "All Files (*.*);; DICOM (*.dcm)")
        print(len(files))
        self.cal_dir_edit.setText(f"{len(files)} files selected")
    
    def get_value(self):
        return str(self.cal_dir_edit.text())

class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super(CentralWidget, self).__init__()
        self.init_ui()
    
    def init_ui(self):
        self.v_layout = QVBoxLayout()
        self.dicom_widget = _DicomWidget()
        self.v_layout.addWidget(self.dicom_widget)
        self.setLayout(self.v_layout)



class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Sphaeroptica")
        print("Hello")
        
        widget = CentralWidget()
        self.setCentralWidget(widget)


        

