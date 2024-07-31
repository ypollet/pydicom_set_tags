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

import base64
import mimetypes

from collections import defaultdict, deque

import pandas as pd
import json

from PySide6.QtCore import (
    QFileInfo
)

import warnings

import pydicom as dicom
from pydicom.datadict import dictionary_VR
from pydicom.tag import Tag
from pydicom.valuerep import VR, FLOAT_VR, INT_VR, STR_VR, BYTES_VR

import requests
from requests.auth import HTTPBasicAuth

import glob

from . import types


TAG_PATIENT = {
    'PatientName',
    'PatientID',
    'PatientBirthDate',
    'PatientSex',
    'OtherPatientIDs'
}
TAG_STUDY = {
    'StudyDate',
    'StudyTime',
    'StudyID',
    'StudyDescription',
    'AccessionNumber',
    'StudyInstanceUID',
    'RequestedProcedureDescription',
    'InstitutionName',
    'RequestingPhysician',
    'ReferringPhysicianName',
}
TAG_SERIES = {
    'SeriesDate',
    'SeriesTime',
    'Modality',
    'Manufacturer',
    'StationName',
    'SeriesDescription',
    'BodyPartExamined',
    'SequenceName',
    'ProtocolName',
    'SeriesNumber',
    'CardiacNumberOfImages',
    'ImagesInAcquisition',
    'NumberOfTemporalPositions',
    'NumberOfSlices',
    'NumberOfTimeSlices',
    'SeriesInstanceUID',
    'ImageOrientationPatient',
    'SeriesType',
    'OperatorsName',
    'PerformedProcedureStepDescription',
    'AcquisitionDeviceProcessingDescription',
    'ContrastBolusAgent',
}

class OrthancRequestError(Exception):
    """Raised when an Orthanc Request didn't pass

    Attributes:
        reason : str
        json
    """
    
    def __init__(self, details, message, json, file) -> None:
        super().__init__()
        self.details = details
        self.message = message
        self.json = json
        self.file = file
        
    def __str__(self) -> str:
        return f"The Request failed for {self.file} for the following reason : {self.message}\n{self.details}"
        
class OrthancProcessError(OrthancRequestError):
    """Raised when an Orthanc Request didn't pass

    Attributes:
        reason : str
        json
    """
    
    def __init__(self, details, message, json, file, series) -> None:
        super().__init__(details, message, json, file)
        self.series = series
    
    def __str__(self) -> str:
        return f"The Request failed for {self.file} of {self.series} for the following reason : {self.message}\n{self.details}"


FILE_NAME = "Label"
STATUS_OK = 200

basic = HTTPBasicAuth('orthanc', 'orthanc')

def encode_file(file : QFileInfo):
    with open(file.absoluteFilePath(), 'rb') as file_to_convert:
        return  base64.b64encode(file_to_convert.read())
    
def to_data_uri(file : QFileInfo):
    encoded_string = encode_file(file)
    
    mime = mimetypes.guess_type(file.absoluteFilePath())[0]
    if mime == None:
        mime = "application/octet-stream"    
    # There's a mime type
    return f"data:{mime};base64,{encoded_string.decode('utf-8')}"

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
    with open(tags.absoluteFilePath(), "+r") as f:
        tags_json : dict = json.load(f)
    
    potential_bad_tags = defaultdict(lambda : defaultdict(lambda: defaultdict(lambda: set())))
    dict_tags = dict()
    
    for study_name, study in tags_json.items():
        study_tags = {}
        for series_name, series in study.items():
            series_tags = []
            for file_name, file_info in series["files"].items():
                dicom_tags = dict()
                for tag_name, val in file_info["tags"].items():
                    try:
                        #Check that all the columns (except the name of the file) are DICOM Standard tags
                        tag = Tag(tag_name)
                        dicom_tags[tag_name] = check_cast(dictionary_VR(tag), val)
                    except:
                        # Error Column name not a valid Name but possibly a private tag
                        potential_bad_tags[study_name][series_name][file_name].add(tag_name)    
                        dicom_tags[tag_name] = val
                series_tags.append((file_name, dicom_tags))
            study_tags[series_name] = series_tags
        dict_tags[study_name] = study_tags
    
    
    # dicts : Series -> file -> tag
    return dict_tags, potential_bad_tags

def check_tag(tag_name : str, val):
    try:
        #Check that all the columns (except the name of the file) are DICOM Standard tags
        tag = Tag(tag_name)
        return True, check_cast(dictionary_VR(tag), val)
    except:
        # Error Column name not a valid Name but possibly a private tag
        return False, val

def send_request(file : QFileInfo, tags : dict, parent : str, instance_number : int = 1) -> dict:
    if(not file.exists()):
        raise OrthancRequestError("Bad Request", {'HttpStatus': 400, 'Details': "File doesn't exists"},file.fileName())
    try:
        tags["InstanceNumber"] = f"{instance_number}"
        ext = file.suffix()
        if ext in types.extension:
            return create_nexus(file, tags, parent)
        else:
            return create_dicom(file, tags, parent)
    except requests.exceptions.HTTPError as e:
        print(e.response.reason)
        print(e.response.json())
        raise OrthancRequestError(e.response.json()["Details"], e.response.json()["Message"], e.response.json(), file.fileName())
    
def get_patient_module(id : str):
    r = requests.get(f'http://localhost:8042/patients/{id}/module', auth=basic)
    r.raise_for_status()
    set_tags = {info['Name']:info["Value"] for tag, info in r.json().items()}
    return set_tags

def get_study_module(id : str):
    r = requests.get(f'http://localhost:8042/studies/{id}/module', auth=basic)
    r.raise_for_status()
    set_tags = {info['Name']:info["Value"] for tag, info in r.json().items()}
    return set_tags
    
def get_series_module(id : str):
    r = requests.get(f'http://localhost:8042/series/{id}/module', auth=basic)
    r.raise_for_status()
    set_tags = {info['Name']:info["Value"] for tag, info in r.json().items()}
    return set_tags

def delete_instance(id : str):
    print(f"Delete Instance : {id}")
    r = requests.delete(f'http://localhost:8042/instances/{id}', auth=basic)

    r.raise_for_status()
    return r.json()

def delete_series(id : str):
    print(f"Delete series : {id}")
    r = requests.delete(f'http://localhost:8042/series/{id}', auth=basic)

    r.raise_for_status()
    return r.json()

def delete_studies(id : str):
    print(f"Delete studies : {id}")
    r = requests.delete(f'http://localhost:8042/studies/{id}', auth=basic)

    r.raise_for_status()
    return r.json()
    
def create_nexus(file : QFileInfo, tags : dict, parent : str) -> dict:
    # Is file with .nxs and .nxz format
    params = {
        'Content' : encode_file(file).decode('utf-8'),
        'Tags' : tags,
    }
    if parent:
        params["Parent"] = parent

    r = requests.post(f'http://localhost:8042/{types.FileAPI.NEXUS.value}', auth=basic, data=json.dumps(params))

    r.raise_for_status()
    return r.json()
    

def create_dicom(file : QFileInfo, tags : dict, parent : str) -> dict:
    content = None
    if file.isFile():
        content = to_data_uri(file)
    else:
        if file.isDir():
            content = []
            list_files = glob.glob(f"{file.absoluteFilePath()}/*")
            for f in list_files:
                content.append(to_data_uri(QFileInfo(f)))
    params = {
        'Content' : content,
        'Tags' : tags,
    }
    if parent:
        params["Parent"] = parent
    if content:
        r = requests.post(f'http://localhost:8042/{types.FileAPI.DICOM.value}', auth=basic, data=json.dumps(params))

        r.raise_for_status()
        response_json = r.json()
        if file.isDir():
            parent_study_json = get_parent_study(response_json["ID"])
            response_json["ParentSeries"] = response_json["ID"]
            response_json["ParentStudy"] = parent_study_json["ID"]
            response_json["ParentPatient"] = parent_study_json["ParentPatient"]
        return response_json
    return None
        
def get_parent_study(id : str):
    r = requests.get(f'http://localhost:8042/series/{id}/study', auth=basic)
    r.raise_for_status()
    return r.json()
    

def update_tags_dicom(files : list[QFileInfo], tags : QFileInfo):
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
        ds.save_as(dicom_file.absoluteFilePath())
    
    warnings.resetwarnings()
    return 0

if __name__ == '__main__':
    file = "../data/images/dicoms.txt"

    dict_tags, potential_tags = check_tags(QFileInfo(file))