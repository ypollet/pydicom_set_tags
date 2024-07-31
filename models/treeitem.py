# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from enum import Enum

from scripts import tags

from PySide6.QtGui import (
    QIcon,
)
class Correspondence(Enum):
    CORRECT = QIcon("images/status.png")
    NOT_PRESENT = QIcon("images/status-busy.png")
    NOT_CORRECT = QIcon("images/status-away.png")
    

class TreeItem:
    def __init__(self, data: list, parent: 'TreeItem' = None, in_tags : Correspondence = Correspondence.NOT_CORRECT, tags_dict = None, potential_bad_tags = None):
        self.item_data = data
        self.is_in_tags = in_tags
        self.parent_item : 'TreeItem' = parent
        self.child_items : list['TreeItem'] = []
        self.tags_dict : dict = tags_dict or dict()
        self.potential_bad_tags : list = potential_bad_tags or []

    def child(self, number: int) -> 'TreeItem':
        if number < 0 or number >= len(self.child_items):
            return None
        return self.child_items[number]

    def last_child(self) -> 'TreeItem':
        return self.child_items[-1] if self.child_items else None

    def child_count(self) -> int:
        return len(self.child_items)

    def child_number(self) -> int:
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def column_count(self) -> int:
        return len(self.item_data)

    def data(self, column: int):
        if column < 0 or column >= len(self.item_data):
            return None
        return self.item_data[column]
    
    def set_tags(self, tags_dict : dict):
        casted_tags = dict()
        for tag_name, tag_val in tags_dict.items():
            is_correct, tag_val = tags.check_tag(tag_name, tag_val)
            if not is_correct:
                self.potential_bad_tags.append(tag_name)
            casted_tags[tag_name] = tag_val
        self.tags_dict = casted_tags

    def insert_children(self, position: int, count: int, columns: int) -> bool:
        if position < 0 or position > len(self.child_items):
            return False

        for row in range(count):
            data = [None] * columns
            item = TreeItem(data.copy(), self)
            self.child_items.insert(position, item)
        return True

    def insert_columns(self, position: int, columns: int) -> bool:
        if position < 0 or position > len(self.item_data):
            return False

        for column in range(columns):
            self.item_data.insert(position, None)

        for child in self.child_items:
            child.insert_columns(position, columns)

        return True

    def parent(self):
        return self.parent_item

    def remove_children(self, position: int, count: int) -> bool:
        if position < 0 or position + count > len(self.child_items):
            return False

        for row in range(count):
            self.child_items.pop(position)

        return True

    def remove_columns(self, position: int, columns: int) -> bool:
        if position < 0 or position + columns > len(self.item_data):
            return False

        for column in range(columns):
            self.item_data.pop(position)

        for child in self.child_items:
            child.remove_columns(position, columns)

        return True

    def set_data(self, column: int, value):
        if column < 0 or column >= len(self.item_data):
            return False

        self.item_data[column] = value
        return True

    def is_correct(self):
        return self.is_in_tags == Correspondence.CORRECT
    
    def set_in_tags(self, in_tags : Correspondence):
        self.is_in_tags = in_tags
            

    def __repr__(self) -> str:
        result = f"<treeitem.TreeItem at 0x{id(self):x}"
        for d in self.item_data:
            result += f' "{d}"' if d else " <None>"
        result += f", {len(self.child_items)} children>"
        return result
