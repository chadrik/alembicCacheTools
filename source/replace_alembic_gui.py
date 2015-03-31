import os
import pymel.core as pm


from PySide import QtGui, QtCore
from PySide.QtGui import QApplication, QMainWindow, QMessageBox

from asset_manager import AssetManager
from file_manager import FileManager
from replace_alembic import ReplaceAlembic
from ui import UI

uiFile = "C:/Users/kei.ikeda/Documents/maya/2014-x64/scripts/replace.ui"

#load ui file
ui = UI()
form_class, base_class = ui.loadUiType(uiFile)

class ReplaceAlembicUi(form_class, base_class):
    def __init__(self, parent = ui.getMayaWindow()):
        super(ReplaceAlembicUi, self).__init__(parent)
        self.setupUi(self)
        
        #create additional controls if necessary
        self.create_controls()
        
        #create connections 
        self.create_connections()
        
    def create_controls(self):
        """ create additional controls if necessary """
        
        self.msgBox = QMessageBox()
        
    def create_connections(self):
        """ create connections """
        
        self.cancelButton.clicked.connect(self.close_dialog)
        self.cancelButton_2.clicked.connect(self.close_dialog)
        self.replaceButton.clicked.connect(self.replace_newer_cache_dialog)
        self.replaceButton_2.clicked.connect(self.replace_another_cache_dialog)
        self.openButton.clicked.connect(self.open_file_dialog)
        self.requestButton.clicked.connect(self.update_cache_dialog)
        
##########################################################################################################
# SLOTS
##########################################################################################################
    def close_dialog(self):
        """ close this dialog """
        self.close()
        
    def open_file_dialog(self):
        """ open file dialog for user to pick cache file to replace with """
        
        fileName, _ = QtGui.QFileDialog.getOpenFileName(self, "Open file", "C:/", "Files (*.abc)")
        
        print fileName
        if fileName:
            self.filePathLineEdit.setText(fileName)
    
    def update_cache_dialog(self):
        """ update label if found any most recent cache for the shot """
        
        #Initialize class
        fm = FileManager()
        am = AssetManager()
        
        #Initialize Variable 
        latestAlem = ""
        currentAlem = ""
        dir = ""
        ext = "abc"
        
        #get all geo_grps
        geoGrps = am.get_geo_grps(pm.listNamespaces())
        
        #Error handle for no geo_grps
        if len(geoGrps) == 0:
            self.msgBox.setText("No geo_grps in scene. Please create reference")
            self.msgBox.exec_()
            return
        
        #obtain the alembic file from alembic attribute
        currentAlem = self.get_alembic_file_path_from_attribute(geoGrps)
        
        #Error handling for failure to obtain the alembic file from alembic attribute
        if currentAlem is None:
            self.msgBox.setText("Failure! Please make sure any geo_grp has extra attribue for alembic")
            self.msgBox.exec_()
            return
            
        #Error handle for existence of path
        if not os.path.exists(currentAlem):
            self.msgBox.setText("Failure! {} does not exist".format(currentAlem))
            self.msgBox.exec_()
            return
        
        #get the directory from the current alembic file 
        dir = fm.get_directory(currentAlem)
        
        #Error handling for failure to obtain the latest alembic cache for this shot
        if fm.get_latest_version_file(dir, ext) is None:
            self.msgBox.setText("Failure! Could not get latest alembic cache. No cache in given directory: {}".format(dir))
            self.msgBox.exec_()
            return
        
        #obtain the latest alembic file
        self.latestAlem = os.path.join(dir, fm.get_latest_version_file(dir, ext)).replace('\\', '/')
                
        if not os.path.exists(self.latestAlem):
            self.msgBox.setText("Failure! {} does not exist".format(self.latestAlem))
            self.msgBox.exec_()
            return
            
        #Compare with version number. Should we compare with its modified date of the file as well?
        if self.is_available_to_update(currentAlem, self.latestAlem):
            self.resultLabel.setText(fm.get_tail(self.latestAlem))
        else:
            self.resultLabel.setText("This is the latest cache!")
            
            
    def get_alembic_file_path_from_attribute(self, geoGrps):
        """ 
        return alembic file path from attribute at one of geometry groups if found any
        
        """
        for geo in geoGrps:
            geoObj = pm.general.PyNode(geo)
            alembicFilePath = geoObj.alembic.get()
            if alembicFilePath: return alembicFilePath
            
        return None
         
    def is_available_to_update(self, currFilePath, latestFilePath):
        """ 
        compare between both files. 
        If latestFilePath version is bigger than currFilePath, return True which means it's available to update. 
        If not, return False
        """
        
        #Initialize class
        fm = FileManager()
        
        if fm.get_version(latestFilePath) > fm.get_version(currFilePath): return True
        return False
       
    def add_attri(self, newAbcFilePath):
        """ update alembic attribute """
        
        #add alembic attribute for each geometry
        am = AssetManager()
        
        #get all geo_grps
        geoGrps = am.get_geo_grps(pm.listNamespaces())
        
        for geo in geoGrps:
            pm.addAttr(geo, longName="alembic", dt="string")
            alembicAttr = '{}.alembic'.format(geo)
            print "alembicAttr: {}".format(alembicAttr)
            pm.setAttr(alembicAttr, newAbcFilePath)
            
            
    def replace_newer_cache_dialog(self):
        """ replace current cache with newer cache """
        
        #initialize class 
        am = AssetManager()
        
        #get all geo_grps
        geoGrps = am.get_geo_grps(pm.listNamespaces())
                
        #replace cache with newer cache
        self.replace_cache(geoGrps, self.latestAlem)
        
        
    def replace_another_cache_dialog(self):
        """ replace current cache with cache picked by user """
        
        #initialize class
        am = AssetManager()
        
        #get geometry groups
        geoGrps = am.get_geo_grps(pm.listNamespaces())
        
        cacheFilePath = str(self.filePathLineEdit.text())
        
        self.replace_cache(geoGrps, cacheFilePath) 
        
        
    def replace_cache(self, geoGrps, cacheFilePath):
        """ replace cache """
        
        #initialize class
        rep = ReplaceAlembic()
        
        #initialize variable
        hasRenderLayers = False
        
        #Check if there are render layers
        if self.renderLayersCheckBox.isChecked(): hasRenderLayers = True
        else: hasRenderLayers = False
        
        print cacheFilePath
        #Error handle for the cache file path does not exist
        if not os.path.exists(cacheFilePath):
            self.msgBox.setText("The cache file does not exist")
            self.msgBox.exec_()
            return
            
            
        #Error handle for no geo_grps
        if len(geoGrps) == 0:
            self.msgBox.setText("No geo_grps in scene. Please create reference")
            self.msgBox.exec_()
            return
            
            
        #close this dialog
        self.close_dialog()
        
        #replace with cache file user requests
        rep.replace_cache(geoGrps, cacheFilePath, hasRenderLayers)
        
        #add extra attribute with its name 'alembic' to hold the new cache file path
        self.add_attri(cacheFilePath)
        
        #let user know it went successfully 
        self.msgBox.setText("Success! It's replaced with {}".format(cacheFilePath))
        self.msgBox.exec_()
        
        
        
if __name__ == "__main__":
    try:
        dialog.deleteLater()
    except:
        pass
    dialog = ReplaceAlembicUi()
    
    try:
        dialog.show()
    except:
        dialog.deleteLater()
        traceback.print_exc()
