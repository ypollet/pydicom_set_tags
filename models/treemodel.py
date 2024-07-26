# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause


from PySide6.QtCore import QModelIndex, Qt, QAbstractItemModel, QDir
from models.treeitem import TreeItem, Correspondence
from scripts import tags
import json
import os

from PySide6.QtGui import (
    QIcon,
)



class TreeModel(QAbstractItemModel):

    def __init__(self, headers: list, directory : QDir=None, parent=None):
        super().__init__(parent)

        self.root_data = headers
        self.root_item = TreeItem(self.root_data.copy())
        
        print(os.getcwd())
        self.ok = QIcon(f"{os.getcwd()}/images/status.png")
        self.warning = QIcon(f"{os.getcwd()}/images/status-busy.png"),
        self.nope = QIcon(f"{os.getcwd()}/images/status-away.png"),
        
        self.setModel(directory)        

    def columnCount(self, parent: QModelIndex = None) -> int:
        return self.root_item.column_count()

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None
        item: TreeItem = self.get_item(index)
        if role == Qt.ItemDataRole.DisplayRole:
            return item.data(index.column())
        if role == Qt.ItemDataRole.DecorationRole:
            print(f"{item.data(0)} : {item.is_in_tags}")
            match item.is_in_tags:
                case Correspondence.CORRECT:
                    print("ok")
                    return self.ok
                case Correspondence.NOT_CORRECT:
                    print("warning")
                    return self.warning
                case Correspondence.NOT_PRESENT:
                    print("nope")
                    return self.nope
        
        return None
    

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return QAbstractItemModel.flags(self, index)

    def get_item(self, index: QModelIndex = QModelIndex()) -> TreeItem:
        if index.isValid():
            item: TreeItem = index.internalPointer()
            if item:
                return item

        return self.root_item

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.root_item.data(section)

        return None

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return QModelIndex()

        child_item: TreeItem = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def insertColumns(self, position: int, columns: int,
                      parent: QModelIndex = QModelIndex()) -> bool:
        self.beginInsertColumns(parent, position, position + columns - 1)
        success: bool = self.root_item.insert_columns(position, columns)
        self.endInsertColumns()

        return success

    def insertRows(self, position: int, rows: int,
                   parent: QModelIndex = QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return False

        self.beginInsertRows(parent, position, position + rows - 1)
        column_count = self.root_item.column_count()
        success: bool = parent_item.insert_children(position, rows, column_count)
        self.endInsertRows()

        return success

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child_item: TreeItem = self.get_item(index)
        if child_item:
            parent_item: TreeItem = child_item.parent()
        else:
            parent_item = None

        if parent_item == self.root_item or not parent_item:
            return QModelIndex()

        return self.createIndex(parent_item.child_number(), 0, parent_item)

    def removeColumns(self, position: int, columns: int,
                      parent: QModelIndex = QModelIndex()) -> bool:
        self.beginRemoveColumns(parent, position, position + columns - 1)
        success: bool = self.root_item.remove_columns(position, columns)
        self.endRemoveColumns()

        if self.root_item.column_count() == 0:
            self.removeRows(0, self.rowCount())

        return success

    def removeRows(self, position: int, rows: int,
                   parent: QModelIndex = QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return False

        self.beginRemoveRows(parent, position, position + rows - 1)
        success: bool = parent_item.remove_children(position, rows)
        self.endRemoveRows()

        return success

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return 0
        return parent_item.child_count()

    def setData(self, index: QModelIndex, value, role: int) -> bool:
        if role != Qt.ItemDataRole.EditRole:
            return False

        item: TreeItem = self.get_item(index)
        result: bool = item.set_data(index.column(), value)

        if result:
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])

        return result

    def setHeaderData(self, section: int, orientation: Qt.Orientation, value,
                      role: int = None) -> bool:
        if role != Qt.ItemDataRole.EditRole or orientation != Qt.Orientation.Horizontal:
            return False

        result: bool = self.root_item.set_data(section, value)

        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result
    
    def setModel(self, directory : QDir | None):
        
        self.directory = directory
        if not directory:
            # directory is None
            return
        json_dir = QDir(directory)
        json_dir.setFilter(QDir.Filter.Files)
        json_dir.setNameFilters(["*.json"])
        
        list_json = json_dir.entryInfoList()
        
        if len(list_json) != 1:
            # send error
            return
        
        self.directory = directory
        studies = self.directory.entryInfoList(filters=QDir.Filter.Dirs| QDir.Filter.NoDotAndDotDot)
        
        series_files = {study.fileName():{series.fileName():[sub for sub in QDir(series.absoluteFilePath()).entryList(filters=QDir.Filter.Dirs | QDir.Filter.Files |QDir.Filter.NoDotAndDotDot)] for series in QDir(study.absoluteFilePath()).entryInfoList(filters=QDir.Filter.Dirs | QDir.Filter.Files |QDir.Filter.NoDotAndDotDot)} for study in studies}
        
        tags_file = list_json[0]
        with open(tags_file.absoluteFilePath(), "+r") as f:
            tags_json : dict = json.load(f)
        self.setupModelData(series_files, tags_json, self.root_item)
        
        

    def setupModelData(self, studies: dict[str, dict[str, set[str]]], tags_dict : dict, root: TreeItem):
        for study in studies.keys() :
            print(f"{study}")
            root.insert_children(root.child_count(),1, self.root_item.column_count())
            study_item = root.last_child()
            study_item.set_data(0, study)
            study_present = study in tags_dict
            study_all_correct = study_present
            for series in studies[study].keys():
                study_item.insert_children(study_item.child_count(),1, self.root_item.column_count())
                print(f"--{series}")
                series_item = study_item.last_child()
                series_item.set_data(0, series)
                series_present = False if not study_present else series in tags_dict[study]
                series_all_correct = series_present
                for file in studies[study][series]:
                    print(f"----{file}")
                    series_item.insert_children(series_item.child_count(),1, self.root_item.column_count())
                    file_item = series_item.last_child()
                    file_item.set_data(0, file)
                    file_item.set_in_tags(Correspondence.CORRECT if series_present and file in tags_dict[study][series]["files"] else Correspondence.NOT_PRESENT)
                    print(f"----{file_item.is_in_tags}")
                    if file_item.is_correct():
                        file_item.set_tags(tags_dict[study][series]["files"][file])
                    else:
                        series_all_correct = False
                
                series_item.set_in_tags(Correspondence.CORRECT if series_all_correct else Correspondence.NOT_CORRECT if series_present else Correspondence.NOT_PRESENT)
                print(f"--{series_item.is_in_tags}")
                if not series_item.is_correct():
                    study_all_correct = False
            
            study_item.set_in_tags(Correspondence.CORRECT if study_all_correct else Correspondence.NOT_CORRECT if study_present else Correspondence.NOT_PRESENT)
            print(f"{study_item.is_in_tags}")
        self.layoutChanged.emit()
        

    def _repr_recursion(self, item: TreeItem, indent: int = 0) -> str:
        result = " " * indent + repr(item) + "\n"
        for child in item.child_items:
            result += self._repr_recursion(child, indent + 2)
        return result

    def __repr__(self) -> str:
        return self._repr_recursion(self.root_item)
