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
    QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QLabel, QPushButton, QListView, QAbstractItemView, QTreeView,
    QSizePolicy, QMenu
)

from PySide6.QtCore import (
    Qt, QFileInfo, QSize, QAbstractListModel, Signal, QDir
)

from PySide6.QtGui import (
    QContextMenuEvent,
    QBrush,
    QPalette,
    QIcon,
    QAction
)

from scripts import tags
import glob
from collections import defaultdict
from models.treemodel import TreeModel
       
    
class _FileWidget(QTreeView):
    
    def __init__(self, parent=None, model : TreeModel=None):
        
        super(_FileWidget, self).__init__(parent)
        self.full_layout = QHBoxLayout()
        self.setLayout(self.full_layout)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.files_model = model
    
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        print(event.globalPos())
        menu = QMenu()
        action = QAction("delete rows")
        menu.addAction(action)
        selectedAction : QAction = menu.exec(event.globalPos())
        print(selectedAction)
        if selectedAction is not None:
            print(f"Delete rows")
            self.files_model.remove_selected_rows(self.selectedIndexes())
        
        


class _DicomWidget(QWidget):
    """_Widget asking for the DICOM files that needs to have tags
    """

    def __init__(self, model : TreeModel,parent=None):
        super(_DicomWidget, self).__init__(parent)
        self.parent = parent
        # Choice of Directory
        full_layout = QVBoxLayout()

        get_dir = QHBoxLayout()
        label = QLabel("Dicom Files : ")
        get_dir.addWidget(label)
                
        
        directories = QPushButton(text="Add directory",parent=self)
        directories.clicked.connect(self.open_directory)
        
        delete = QPushButton(text="Delete items",parent=self)
        delete.clicked.connect(self.delete_items)

        get_dir.addWidget(directories)
        get_dir.addWidget(delete)
        get_dir.setSpacing(20)
        
        full_layout.addLayout(get_dir)
        
        self.list_files = _FileWidget(parent=self, model=model)
        self.list_files.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.list_files.setMinimumSize(QSize(300,300))
        self.list_files.setBackgroundRole(QPalette.ColorRole.AlternateBase)
        self.series_model = model
        self.list_files.setModel(self.series_model)
        full_layout.addWidget(self.list_files)
        
        get_dir.setContentsMargins(20,0,100,0)
        self.setLayout(full_layout)
        
    def open_directory(self):
        directory = QDir(QFileDialog.getExistingDirectory(self, "Select Directory"))   
        self.series_model.setModel(directory)
            
    def delete_items(self):
        indexes = sorted(self.list_files.selectedIndexes(), reverse=True)
        self.series_model.remove_selected_rows(indexes)


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super(CentralWidget, self).__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.v_layout = QVBoxLayout()
        
        print("Create Model")
        self.model = TreeModel(["Orthanc"])

        print("Create Dicom")
        self.dicom_widget = _DicomWidget(model=self.model, parent=self)
        self.v_layout.addWidget(self.dicom_widget)

        self.update_button = QPushButton("Update Tags")
        self.update_button.clicked.connect(self.update_tags)
        self.v_layout.addWidget(self.update_button)

        self.setLayout(self.v_layout)

    def update_tags(self):
        if(len(self.model.studies) > 0 and len(self.model.dicom_tags) > 0):
            tags.send_requests(self.model.studies, self.model.series_files, self.model.dicom_tags)


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        print("MainWindow")
        self.setWindowTitle("Dicomizer")
        
        widget = CentralWidget()
        self.setCentralWidget(widget)


        

