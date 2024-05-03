# Canathist Automizer Tags 2023

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


from logging.handlers import QueueHandler

import sys
# setting path
sys.path.append('./GUI')

from typing import Tuple
from PySide6.QtWidgets import (
    QApplication
)

import GUI.main as main

app = QApplication(sys.argv)
w = main.MainWindow()
w.show()
app.exec()