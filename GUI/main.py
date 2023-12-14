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

from PySide6.QtCore import (
    Qt, QFileInfo
)

from scripts import update_tags as ut

class _TagsWidget(QWidget):
    """_Widget asking for the csv file containing tags
    """

    def __init__(self,parent=None):
        super(_TagsWidget, self).__init__(parent)
        self.parent = parent
        # Choice of Directory
        get_dir = QHBoxLayout()
        label = QLabel("Tags file : ")
        get_dir.addWidget(label)
        
        self.info_files_added=QLabel("No file selected") 
        get_dir.addWidget(self.info_files_added)
        
        dicom_files = QPushButton(text="Browse...",parent=self)
        dicom_files.clicked.connect(self.open_directory)

        get_dir.addWidget(dicom_files)
        get_dir.setSpacing(20)
        self.setLayout(get_dir)
        
        get_dir.setContentsMargins(20,0,100,0)

    def open_directory(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select DICOM files", ".", "CSV files (*.csv *.txt)")
        file = str.strip(file)
        if file is None or file == "":
            return
        
        self.csv = QFileInfo(file)
        self.info_files_added.setText(self.csv.fileName())
    
    def get_value(self):
        return self.csv


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

        self.files = []
        
        self.info_files_added=QLabel("No files selected") 
        get_dir.addWidget(self.info_files_added)
        
        dicom_files = QPushButton(text="Browse...",parent=self)
        dicom_files.clicked.connect(self.open_directory)

        get_dir.addWidget(dicom_files)
        get_dir.setSpacing(20)
        self.setLayout(get_dir)
        
        get_dir.setContentsMargins(20,0,100,0)

    def open_directory(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select DICOM files", ".", "DICOM files (*.dcm)")
        print(len(files))

        self.files = [QFileInfo(x) for x in files]
        self.info_files_added.setText(f"{len(files)} files selected")
    
    def get_value(self):
        return self.files


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super(CentralWidget, self).__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.v_layout = QVBoxLayout()

        self.dicom_widget = _DicomWidget()
        self.v_layout.addWidget(self.dicom_widget)

        self.tags_widget = _TagsWidget()
        self.v_layout.addWidget(self.tags_widget)

        self.update_button = QPushButton("Update Tags")
        self.update_button.clicked.connect(self.update_tags)
        self.v_layout.addWidget(self.update_button)

        self.setLayout(self.v_layout)

    def update_tags(self):
        ut.update_tags(self.dicom_widget.get_value(), self.tags_widget.get_value())


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Sphaeroptica")
        
        widget = CentralWidget()
        self.setCentralWidget(widget)


        

