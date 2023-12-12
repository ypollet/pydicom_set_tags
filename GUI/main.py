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
    QMainWindow, QStackedLayout, QWidget, QVBoxLayout, QFileDialog, QCheckBox
)
from PySide6.QtGui import (
    QAction, QIcon
)
from PySide6.QtCore import (
    QSettings, Qt
)

class MyDialog(QFileDialog):
    def __init__(self, parent=None):
        super (MyDialog, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.v_layout = QVBoxLayout()
        cb = QCheckBox('Select directory')
        cb.stateChanged.connect(self.toggle_files_folders)
        self.v_layout.addWidget(cb)

        self.setLayout(self.v_layout)

    def toggle_files_folders(self, state):
        if state == Qt.CheckState.Checked:
            self.setFileMode(self.FileMode.Directory)
            self.setOption(self.Option.ShowDirsOnly, True)
        else:
            self.setFileMode(self.FileMode.AnyFile)
            self.setOption(self.Option.ShowDirsOnly, False)
            self.setNameFilter('All files (*)')

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Sphaeroptica")
        print("Hello")
        
        widget = MyDialog()
        self.setCentralWidget(widget)


        

