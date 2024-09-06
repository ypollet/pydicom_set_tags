# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause


from PySide6.QtCore import QModelIndex, Qt, QAbstractItemModel, QDir, QFileInfo

from scripts import tags
import json
import os

from PySide6.QtGui import (
    QIcon,
)

from models.treeitem import TreeItem, Correspondence, RequestType
from GUI.Error_Messages.change_module_value import WrongValue, WrongValueDialog
from GUI.Error_Messages.not_all_correct import NotAllCorrectDialog
from GUI.Error_Messages.request_exception import RequestExceptionDialog




class TreeModel(QAbstractItemModel):

    def __init__(self, headers: list, directory : QDir=None, parent=None):
        super().__init__(parent)

        self.root_data = headers
        self.root_item = TreeItem(self.root_data.copy())
        
        print(os.getcwd())
        self.ok = QIcon(f"{os.getcwd()}/images/status.png")
        self.warning = QIcon(f"{os.getcwd()}/images/status-busy.png")
        self.nope = QIcon(f"{os.getcwd()}/images/status-away.png")
        
        self.setModel(directory)        

    def columnCount(self, parent: QModelIndex = None) -> int:
        return self.root_item.column_count()

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None
        item: TreeItem = self.get_item(index)
        if role == Qt.ItemDataRole.DisplayRole:
            return item.data(index.column())
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            return item.is_in_tags.value
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

    def removeSelectedRows(self, rows : list[QModelIndex] = None):
        if not rows or len(rows) == 0:
            return
            
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return 0
        return parent_item.child_count()
    
    def refreshModel(self):
        self.setModel(self.directory)

    def setModel(self, directory : QDir | None):
        # Reset model
        self.reinit()
        
        self.directory = directory
        if not directory:
            # directory is None so don't update non-existent data
            return
        json_dir = QDir(directory)
        json_dir.setFilter(QDir.Filter.Files)
        json_dir.setNameFilters(["*.json"])
        
        list_json = json_dir.entryInfoList()
        
        if len(list_json) != 1:
            # TODO: send error
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
            root.insert_children(root.child_count(),1, self.root_item.column_count())
            study_item = root.last_child()
            study_item.set_data(0, study)
            study_present = study in tags_dict
            study_all_correct = study_present
            for series in studies[study].keys():
                study_item.insert_children(study_item.child_count(),1, self.root_item.column_count())
                series_item = study_item.last_child()
                series_item.set_data(0, series)
                series_present = False if not study_present else series in tags_dict[study]
                if series_present:
                    type_request = RequestType[tags_dict[study][series]["type"]] if "type" in tags_dict[study][series] else RequestType.DEFAULT
                    options = tags_dict[study][series]["options"] if "options" in tags_dict[study][series] else {}
                    series_item.set_request_type(type_request, options)
                series_all_correct = series_present
                for file in studies[study][series]:
                    series_item.insert_children(series_item.child_count(),1, self.root_item.column_count())
                    file_item = series_item.last_child()
                    file_item.set_data(0, file)
                    file_item.set_in_tags(Correspondence.CORRECT if series_present and file in tags_dict[study][series]["files"] else Correspondence.NOT_PRESENT)
                    if file_item.is_correct():
                        file_item.set_tags(tags_dict[study][series]["files"][file]["tags"])
                    else:
                        series_all_correct = False
                
                series_item.set_in_tags(Correspondence.CORRECT if series_all_correct else Correspondence.NOT_CORRECT if series_present else Correspondence.NOT_PRESENT)
                if not series_item.is_correct():
                    study_all_correct = False
            
            study_item.set_in_tags(Correspondence.CORRECT if study_all_correct else Correspondence.NOT_CORRECT if study_present else Correspondence.NOT_PRESENT)
        self.layoutChanged.emit()
    
    def send_requests(self):
        failed_studies = [study.data(0) for study in self.root_item.child_items if not study.is_correct()]
        if(len(failed_studies) > 0):
            msg_box = NotAllCorrectDialog(failed_studies)
            ret = msg_box.exec()
            if not ret:
                return
        
        set_studies = set()
        for study_item in self.root_item.child_items:
            try:
                parent = ""
                parent_study = ""
                
                patient_module = dict()
                study_module = dict()
                if not study_item.is_correct():
                    
                    continue
                for series_item in study_item.child_items:
                    series_module = dict()
                    print(f"Update Series {study_item.data(0)}/{series_item.data(0)}")
                    instance_number = 0
                    for file_item in series_item.child_items:
                        
                        wrong_value_tag = [WrongValue(tag, val_module, file_item.tags_dict[tag]) for tag, val_module in patient_module.items() if (tag in file_item.tags_dict and val_module != file_item.tags_dict[tag])]
                        wrong_value_tag.extend([WrongValue(tag, val_module, file_item.tags_dict[tag]) for tag, val_module in study_module.items() if (tag in file_item.tags_dict and val_module != file_item.tags_dict[tag])])
                        wrong_value_tag.extend([WrongValue(tag, val_module, file_item.tags_dict[tag]) for tag, val_module in series_module.items() if (tag in file_item.tags_dict and val_module != file_item.tags_dict[tag])])
                        print(f"------------ File : {file_item.data(0)} : {wrong_value_tag}")
                        if len(wrong_value_tag) > 0 :
                            msg_box = WrongValueDialog(wrong_value_tag)
                            ret = msg_box.exec()
                            if not ret:
                                self.delete_all_studies(set_studies)
                                self.reinit()
                                return
                        
                        
                        tags_dict = {tag:val for tag, val in file_item.tags_dict.items() if tag not in patient_module and tag not in study_module and tag not in series_module}
                        
                        response = tags.send_request(QFileInfo(f"{self.directory.absoluteFilePath(study_item.data(0))}/{series_item.data(0)}/{file_item.data(0)}"), tags_dict, parent, instance_number)
                        print(response)
                        parent = response["ParentSeries"]
                        parent_study = response["ParentStudy"]
                        instance_id = response["ID"]
                        set_studies.add(parent_study)
                        file_item.set_data(1, instance_id)
                        series_item.set_data(1, parent)
                        study_item.set_data(1, parent_study)
                        
                        patient_module.update({tag:val for tag, val in tags_dict.items() if tag in tags.TAG_PATIENT})
                        study_module.update({tag:val for tag, val in tags_dict.items() if tag in tags.TAG_STUDY})
                        series_module.update({tag:val for tag, val in tags_dict.items() if tag in tags.TAG_SERIES})
                        
                        instance_number += 1
                        self.layoutChanged.emit()
                    parent = parent_study
                
                
            except Exception as e:
                # TODO error handling if error !
                msg_box = RequestExceptionDialog(e)
                ret = msg_box.exec()
                if not ret:
                    self.delete_all_studies(set_studies)
                    self.reinit()
                    return
                else:
                    # only delete the study
                    if parent_study:
                        tags.delete_studies(parent_study)
                
        
        #self.reinit()
        
            
    
    def reinit(self):
        # REINIT MODEL
        self.directory = None
        self.root_item = TreeItem(self.root_data.copy())
        self.layoutChanged.emit()
    
    def delete_all_studies(self, list_studies : list[str]):
        for study in list_studies:
            tags.delete_studies(study)
                
    def _repr_recursion(self, item: TreeItem, indent: int = 0) -> str:
        result = " " * indent + repr(item) + "\n"
        for child in item.child_items:
            result += self._repr_recursion(child, indent + 2)
        return result

    def __repr__(self) -> str:
        return self._repr_recursion(self.root_item)
