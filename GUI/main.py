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
    QMimeData, QModelIndex, QPersistentModelIndex, Qt, QFileInfo, QSize, QAbstractListModel, Signal
)

from PySide6.QtGui import (
    QContextMenuEvent,
    QBrush,
    QPalette,
    QIcon,
    QAction
)

from scripts import tags

class _DicomsModel(QAbstractListModel):
    listChanged = Signal()
    def __init__(self, *args, files=None, **kwargs):
        super(_DicomsModel, self).__init__(*args, **kwargs)
        self.files = files or []
        self.files_check = set()
        self.dicom_tags = dict()
        self.potential_bad_tags = []
        self.files_not_added = set()
        
        self.listChanged.connect(self.check_list)
        
        self.file_icon = QIcon("images/document.png")
        self.folder_icon = QIcon("images/folder.png")

    def data(self, index, role):
        file = self.files[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            # See below for the data structure.
           # Return the todo text only.
            return file.fileName()
        
        if role == Qt.ItemDataRole.DecorationRole:
            if file.isFile():
                return self.file_icon
            if file.isDir():
                return self.folder_icon
        
        if role == Qt.ItemDataRole.BackgroundRole:
            if file.fileName() in self.dicom_tags:
                return QBrush(Qt.GlobalColor.darkGreen)
    
    def check_list(self):
        self.files_not_added = [file for file in self.dicom_tags.keys() if file not in self.files_check]
        self.layoutChanged.emit()

    def rowCount(self, index):
        return len(self.files)
    
    def canDropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex | QPersistentModelIndex) -> bool:     
        return True
    
    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex | QPersistentModelIndex) -> bool:
        if not data.hasUrls() :
            return False
        files = [QFileInfo(u.toLocalFile()) for u in data.urls()]    
        self.add_files(files)
            
        # Trigger refresh.
        self.listChanged.emit()
        
        return True

    def flags(self, index):
        flags = super().flags(index)
        if not index.isValid():
            flags |= Qt.ItemFlag.ItemIsDropEnabled
        return flags

    def remove_selected_rows(self, selectedIndexes : list):
        selectedIndexes = sorted(selectedIndexes, reverse=True)
        for index in selectedIndexes:
            self.files.pop(index.row())
        
        self.listChanged.emit()
    
    def add_files(self, files : list):
        already_in = []
        for f in files:
            if f.fileName() in self.files_check:
                # send error message ?
                already_in.append(f)
            else:
                self.files_check.add(f.fileName())
                self.files.append(f)
        
    
class _DragAndDropFileWidget(QListView):
    
    def __init__(self, parent=None, model : _DicomsModel=None):
        
        super(_DragAndDropFileWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.full_layout = QHBoxLayout()
        self.setLayout(self.full_layout)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.files_model = model

        self.setDropIndicatorShown(True)
    
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

    def __init__(self, model : _DicomsModel,parent=None):
        super(_DicomWidget, self).__init__(parent)
        self.parent = parent
        # Choice of Directory
        full_layout = QVBoxLayout()

        get_dir = QHBoxLayout()
        label = QLabel("Dicom Files : ")
        get_dir.addWidget(label)
                
        files = QPushButton(text="Add Files",parent=self)
        files.clicked.connect(self.open_files)
        
        directories = QPushButton(text="Add directories",parent=self)
        directories.clicked.connect(self.open_directories)
        
        delete = QPushButton(text="Delete items",parent=self)
        delete.clicked.connect(self.delete_items)

        get_dir.addWidget(files)
        get_dir.addWidget(directories)
        get_dir.addWidget(delete)
        get_dir.setSpacing(20)
        
        full_layout.addLayout(get_dir)
        
        self.list_files = _DragAndDropFileWidget(parent=self, model=model)
        self.list_files.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.list_files.setMinimumSize(QSize(300,300))
        self.list_files.setBackgroundRole(QPalette.ColorRole.AlternateBase)
        self.files_model = model
        self.list_files.setModel(self.files_model)
        full_layout.addWidget(self.list_files)
        
        get_dir.setContentsMargins(20,0,100,0)
        self.setLayout(full_layout)

    def open_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select DICOM files", ".", "All Files (*);; Images (*.tif *.jpeg *.jpg *.png);; PDF (*.pdf)")

        files = [QFileInfo(x) for x in files]
        self.files_model.add_files(files)
        # Trigger refresh.
        self.files_model.listChanged.emit()
        
    def open_directories(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        l_view : QListView = dialog.findChild(QListView, "listView")
        if l_view :
            l_view.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        tView : QTreeView = dialog.findChild(QTreeView)
        if tView:
            tView.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        dialog.exec()
        
        directories = [QFileInfo(x) for x in dialog.selectedFiles()]
        self.files_model.add_files(directories)
        self.files_model.listChanged.emit()
    
    def delete_items(self):
        indexes = sorted(self.list_files.selectedIndexes(), reverse=True)
        self.files_model.remove_selected_rows(indexes)

class _TagsWidget(QWidget):
    """_Widget asking for the csv file containing tags
    """

    def __init__(self, model : _DicomsModel, parent=None):
        super(_TagsWidget, self).__init__(parent)
        self.parent = parent
        self.model = model
        # Choice of Directory
        get_dir = QHBoxLayout()
        label = QLabel("Tags file : ")
        get_dir.addWidget(label)
        
        self.info_files_added = QLabel("No file selected") 
        get_dir.addWidget(self.info_files_added)
        
        dicom_files = QPushButton(text="Browse...",parent=self)
        dicom_files.clicked.connect(self.open_files)

        get_dir.addWidget(dicom_files)
        get_dir.setSpacing(20)
           
        self.setLayout(get_dir)
        self.model.listChanged.connect(self.modify_tooltip)
        
        get_dir.setContentsMargins(20,0,100,0)

    def open_files(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select csv file", ".", "CSV files (*.csv *.txt)")
        file = str.strip(file)
        if file is None or (not file.endswith('.txt') and not file.endswith('.csv')):
            return
        
        self.csv = QFileInfo(file)
        self.info_files_added.setText(self.csv.fileName())
        
        self.model.dicom_tags, self.model.potential_bad_tags = tags.check_tags(self.csv)     
        self.model.listChanged.emit()
        print(self.model.dicom_tags)
        for key, _ in self.model.dicom_tags.items():
            print(key)
    
    def modify_tooltip(self):
        if len(self.model.files_not_added) == 0:
            self.setToolTip("")
            return
        
        str = "Files to add : "
        for file in self.model.files_not_added:
            str += f"\n {file}"
        self.setToolTip(str)


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super(CentralWidget, self).__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.v_layout = QVBoxLayout()
        
        self.model = _DicomsModel()

        self.dicom_widget = _DicomWidget(model=self.model, parent=self)
        self.v_layout.addWidget(self.dicom_widget)

        self.tags_widget = _TagsWidget(model=self.model, parent=self)
        self.v_layout.addWidget(self.tags_widget)

        self.update_button = QPushButton("Update Tags")
        self.update_button.clicked.connect(self.update_tags)
        self.v_layout.addWidget(self.update_button)

        self.setLayout(self.v_layout)

    def update_tags(self):
        if(len(self.model.files) > 0 and len(self.model.dicom_tags) > 0):
            tags.create_dicom(self.model)


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Sphaeroptica")
        
        widget = CentralWidget()
        self.setCentralWidget(widget)


        

