import traceback

import maya.OpenMayaUI as omui

from PySide.QtCore import *
from PySide.QtGui import *

import pymel.core as pm
import os
import json

from shiboken import wrapInstance
from asset_manager import AssetManager
from import_alembic import ImportAlembic
from file_manager import FileManager
from reference import Reference

#default window size
IMPORT_WINDOW_WIDTH = 650
IMPORT_WINDOW_HEIGHT = 450

#change here for specific project you want to set in default
CURRENT_PRODUCT = "SampleProject"

#change here when you work on other root
ROOT = "C:\\"

print os.environ

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QWidget)

class importAlembicDialog(QDialog):
    
    def __init__(self, parent=maya_main_window()):
        """ initialize """
        super(importAlembicDialog, self).__init__(parent)
        
        
    def create(self):
        """ create the whole ui """
        self.setWindowTitle('Alembic Import')
        self.setFixedSize(IMPORT_WINDOW_WIDTH, IMPORT_WINDOW_HEIGHT)
        self.create_controls()
        self.create_layout()
        self.create_connections()

    def create_controls(self):
        """ create controls such as buttons, labels, etc. """
        
        #Intialize class 
        fm = FileManager()
        
        self.msgBox = QMessageBox()
        
        #Buttons
        self.import_button = QPushButton('Import')
        self.cancel_button = QPushButton('Cancel')
        
        #Labels
        self.product_label = QLabel("Production: ")
        self.sequences_label = QLabel("Sequences: ")
        self.shots_label = QLabel("Shots: ")
        self.refer_label = QLabel()
        
        #check box
        self.camera_check_box = QCheckBox("Import Shot Camera")
        
        #Combo box
        self.combo_box = QComboBox()
        
        #Get data for List Widget
        self.productItems = self.get_products_list(ROOT)
        self.combo_box.addItems(self.productItems)
        defaultIndex = self.productItems.index(CURRENT_PRODUCT)
        self.combo_box.setCurrentIndex(defaultIndex)
        self.sequence_list_wdg = QListWidget()
        selectedProduct = self.productItems[defaultIndex]
        self.sequenceItems = self.get_sequence_list(selectedProduct)
        self.shots_list_wdg = QListWidget()
        selectedSequence = self.sequenceItems[0] # default
        self.shotItems = self.get_shots_list(selectedProduct, selectedSequence)
        
        referenceFilePath = fm.get_reference_file_path(ROOT, selectedProduct, selectedSequence, self.shotItems[0])
         
        if not referenceFilePath: referenceFilePath = "No reference file is found"
        
        self.refer_label.setText(referenceFilePath)
        
        #List Widget for sequence
        self.sequence_list_wdg.addItems(self.sequenceItems)
        self.sequence_list_wdg.setCurrentRow(0)
        self.sequence_list_wdg.setMaximumHeight(100)
       
        #List Widget for shots
        self.shots_list_wdg.addItems(self.shotItems)
        self.shots_list_wdg.setCurrentRow(0)
        self.shots_list_wdg.setMaximumHeight(150)
        
        
    def create_layout(self):
                
        #Button Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.import_button)
        button_layout.addStretch()
        
        #Main Layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(1)
        main_layout.addWidget(self.product_label)
        main_layout.addWidget(self.combo_box)
        main_layout.addWidget(self.sequences_label)
        main_layout.addWidget(self.sequence_list_wdg)
        main_layout.addWidget(self.shots_label)
        main_layout.addWidget(self.shots_list_wdg)
        main_layout.addWidget(self.refer_label)
        main_layout.addWidget(self.camera_check_box)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def create_connections(self):
        """ Create the signal/slot connections """
        
        self.connect(self.cancel_button, SIGNAL('clicked()'), self.close_dialog) 
        self.connect(self.import_button, SIGNAL('clicked()'), self.import_alembic_dialog)
        self.combo_box.currentIndexChanged.connect(self.on_comboBox_changed)
        self.sequence_list_wdg.currentItemChanged.connect(self.on_sequenceList_changed)
        self.shots_list_wdg.currentItemChanged.connect(self.on_shotList_changed)  

        
##################################################################################################
# SLOTS
##################################################################################################

    def on_comboBox_changed(self, currIndex):
        """ update sequence list if combo box for project is changed by user """
        
        self.sequence_list_wdg.clear()
        
        currentProduct = self.productItems[currIndex]
        sequenceItems = self.get_sequence_list(currentProduct)
        self.sequence_list_wdg.addItems(sequenceItems)
        self.sequence_list_wdg.setCurrentRow(0)
        
        
    def on_sequenceList_changed(self, current, previous):
        """ update shot list when one of sequences is selected by user """
        
        self.shots_list_wdg.clear()
        
        if current is not None:
            currProductIndex = self.combo_box.currentIndex()
            selectedProduct = self.productItems[currProductIndex]
            selectedSequence = current.text()
            shotItems = self.get_shots_list(selectedProduct, selectedSequence)
            self.shots_list_wdg.addItems(shotItems)
            self.shots_list_wdg.setCurrentRow(0)
            
        
    def on_shotList_changed(self, current, previous):
        """ update refer_label when one of shots is selected by user """
        
        #initialize class
        fm = FileManager()
        
        if current is not None:
            currProductIndex = self.combo_box.currentIndex()
            currProduct = self.productItems[currProductIndex]
            currShot = current.text()
            currSeq = self.sequence_list_wdg.currentItem().text()
            
            referenceFilePath = fm.get_reference_file_path(ROOT, currProduct, currSeq, currShot)
            
            if not referenceFilePath: referenceFilePath = "No reference file is found"
            
            self.refer_label.setText(referenceFilePath)
        
    
    def get_products_list(self, root):
        """ get list of products/projects such as uCoolProject from given root """
        
        return [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    
    
    
    def get_sequence_list(self, selectedProduct):
        """ get list of sequence such as 0100 from given product/project """
        
        path = os.path.join(ROOT, selectedProduct)
        
        path = os.path.join(path, "production")
        
        path = os.path.join(path, "sequences")
        
        sequenceList = []
        
        if os.path.exists(path):
            dirs = next(os.walk(path))[1]
            for d in dirs:
                if d.isdigit():
                    sequenceList.append(d)
            return sequenceList
        else:
            return []
        
    def get_shots_list(self, selectedProduct, selectedSequence):
        """ get list of shot such as 0100_0230 from given product/project and sequence """
        
        path = os.path.join(ROOT, selectedProduct)
        path = os.path.join(path, "production")
        path = os.path.join(path, "sequences")
        path = os.path.join(path, selectedSequence)
        
        sequenceList = []
        
        if os.path.exists(path):
            dirs = next(os.walk(path))[1]
            for d in dirs:
                if ((d.split('_'))[0].isdigit()):
                    sequenceList.append(d)
            return sequenceList
        else:
            return []
            
        
    def import_alembic_dialog(self):
        """ Import alembic once we recieve data from reference file """ 
        
        #Initialize classes 
        ia = ImportAlembic()
        fm = FileManager()
        am = AssetManager()
        
        #Get data from GUI
        currProductIndex = self.combo_box.currentIndex()
        currProduct = self.productItems[currProductIndex]
        currShot = self.shots_list_wdg.currentItem().text()
        currSeq = self.sequence_list_wdg.currentItem().text()
        
        #Create reference file path from data 
        referenceFilePath = fm.get_reference_file_path(ROOT, currProduct, currSeq, currShot)
        
        #Error handling if reference file is empty
        if referenceFilePath is None:
            self.msgBox.setText("Animation has not been exported yet")
            self.msgBox.exec_()
            return 
        
        #create reference 
        self.create_reference(referenceFilePath)
        
        #get geometry groups to get ready for merge-import
        geoGrps = am.get_geo_grps(pm.listNamespaces())
        
        #Get animation cache file from json file 
        abcFilePath = self.get_alembic_file_from_json(referenceFilePath)
        
        #Import Alembic 
        ia.import_alembic(geoGrps, abcFilePath)
        
        #add alembic attribute for each geometry
        for geo in am.get_geo_grps(pm.listNamespaces()):
            am.add_alembic_attribute(geo, abcFilePath)
        
        #Get animation cache directory to check if shot camera exists 
        directory = os.path.dirname(abcFilePath)
        
        #If camera check box is checked, import shot camera
        if self.camera_check_box.isChecked():
            
            #check if shot camera cache file is in directory
            if fm.has_shot_camera(directory):
                cameraFilePath = fm.get_camera_import_cache_file_path(directory) 
                ia.import_shot_camera(cameraFilePath) 
            else:
                self.msgBox.setText("No ShotCamera cache is Found")
                self.msgBox.exec_()
                return
        
        #show message box to let users know it went successfully
        
        
        self.close()

        
    def create_reference(self, path):
        """ create referebce """
        
        #initialize classes 
        json_file = file(path)
        ref = Reference()
        
        #data is loaded by json file 
        data = json.loads(json_file.read())
        
        for reference in data['reference']:
            nameSpace = reference['name_space']
            shadeCachePath = reference['shader_cache_file_path']
            ref.create_reference(nameSpace, shadeCachePath)
            
            
    def get_alembic_file_from_json(self, path):
        """ get exported animation cache file (abc file) from json file """
        
        #initialize class
        json_file = file(path)
        
        data = json.loads(json_file.read())
        
        return data['reference'][0]['animation_cache_file_path']
        
        
    def close_dialog(self):
        """ close this dialog """
        
        self.close()
        
    
    
if __name__ == "__main__":
    try:
        dialog.deleteLater()
    except:
        pass
    
    dialog = importAlembicDialog()
    
    try:
        dialog.create()
        dialog.show()
    except:
        dialog.deleteLater()
        traceback.print_exc()
        