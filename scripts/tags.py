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

import PIL.Image
import base64
from io import BytesIO

import pandas as pd

from PySide6.QtCore import (
    QFileInfo
)

import warnings

import pydicom as dicom
from pydicom.datadict import dictionary_VR
from pydicom.tag import Tag
from pydicom.valuerep import VR, FLOAT_VR, INT_VR, STR_VR, BYTES_VR

import PIL


FILE_NAME = "Label"
STATUS_OK = 200

def to_data_uri(path):
    img = PIL.Image.open(path)
    im_file = BytesIO()
    img.save(im_file, format=img.format)
    encoded_img = base64.b64encode(im_file.getvalue()) #base64.encodebytes(im_file.getvalue()).decode('ascii')
    base64.b64encode(im_file.getvalue())
    return f"data:image/{img.format};base64,{encoded_img.decode('utf-8')}"

def check_cast(vr, val):
    if vr == VR.AT:
        # if it's an Attribute
        return Tag(val)
    if vr in STR_VR:
        return str(val)
    
    if vr in INT_VR:
        return int(val)
    
    if vr in FLOAT_VR:
        return float(val)
    
    if vr in BYTES_VR:
        return bytes(val)
    
    raise NotImplementedError("cast for SQ not implemented")

def check_tags(tags : QFileInfo):
    print(tags.absoluteFilePath())
    tags_df = pd.read_csv(tags.absoluteFilePath(), delimiter=';')
    print(tags_df)
    
    potential_bad_tags = []
    dict_tags = dict()
    #Check that all the columns (except the name of the file) are DICOM Standard tags
    for tag_name, _ in tags_df.items():
        if tag_name != FILE_NAME:
            try:
                _ = Tag(tag_name)
            except:
                # Error Column name not a valid Name but possibly a private tag
                potential_bad_tags.append(tag_name)
    for index, row in tags_df.iterrows():
        dicom_tags = dict()
        label = row[FILE_NAME]
        
        row_tags = row.drop(FILE_NAME)
        print(label)

        for col, val in row_tags.items():
            dicom_tags[col] = val
        dict_tags[label] = dicom_tags
    return dict_tags, potential_bad_tags       
        

def update_tags(files : list, tags : QFileInfo):
    warnings.filterwarnings("error")
    
    files = {file.baseName():file for file in files}
    tags_df = pd.read_csv(tags.absoluteFilePath(), delimiter=';')      
    
    #Check that all the columns (except the name of the file) are DICOM Standard tags
    for series_name, _ in tags_df.items():
        if series_name != FILE_NAME:
            try:
                tag = Tag(series_name)
            except:
                # Error Column name not valid
                print(f"{series_name} is not a valid tag")
                return -1
    
    print(tags_df.shape)

    for index, row in tags_df.iterrows():
        image_label = row[FILE_NAME]

        if not image_label in files:
            print(f"{image_label} has not been selected")
            continue

        dicom_file = files[image_label]
        
        ds = dicom.read_file(dicom_file.absoluteFilePath())

        row_tags = row.drop(FILE_NAME)

        for col, val in row_tags.items():

            #already checked that the Tag exists
            tag = Tag(col)
            
            try:
                #print(f"{tag} {col} : {dictionary_VR(tag)} with {val} encoded by {type(val)}")
                VR = dictionary_VR(tag)
                ds.add(dicom.DataElement(tag, VR, check_cast(VR,val)))
            except Exception as error:
                print(f"{image_label} : error for {tag} {col} - {val} : {error}")
                #continue even if a tag wasn't added

        print(image_label)
        print(row)
        print(ds)
        print("-----------------------------------------------------------------")
        ds.save_as(dicom_file.absoluteFilePath())
    
    warnings.resetwarnings()
    return 0

if __name__ == '__main__':
    file = "../data/images/dicoms.txt"

    dict_tags, potential_tags = check_tags(QFileInfo(file))