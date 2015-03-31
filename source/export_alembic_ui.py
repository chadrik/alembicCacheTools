import os
import pymel.core as pm

from PySide import QtGui, QtCore
from PySide.QtGui import QApplication, QMainWindow, QMessageBox

from export_alembic import *
from asset_manager import AssetManager
from json_builder import JsonBuilder
from file_manager import FileManager
from ui import UI 


uiFile = "C:/Users/kei.ikeda/Documents/maya/2014-x64/scripts/export.ui"
    
#load ui file
ui = UI()
form_class, base_class = ui.loadUiType(uiFile)

class ExportAlembicUi(form_class, base_class):
    def __init__(self, parent = ui.getMayaWindow()):
        super(ExportAlembicUi, self).__init__(parent)
        
        #set up UI
        self.setupUi(self)
        
        #initialize classes
        self.assetManager = AssetManager()
        
        self.geo_grps = self.assetManager.get_geo_grps(pm.listNamespaces())
        
        #create additional controls 
        self.create_controls()
        
        #create connections
        self.create_connections()
        
        #set default setting 
        self.set_default_setting()
        
        #hide camera setting in the beginning 
        self.hide_camera_setting()
        
    def create_controls(self):
        """ create controls """
        
        self.model = QtGui.QStandardItemModel(self.listView)
        
        for geo in self.geo_grps:
            if geo.startswith(":"): geo = geo[1:]
            item = QtGui.QStandardItem(geo)
            item.setCheckable(True)
            item.setCheckState(QtCore.Qt.Checked)
            self.model.appendRow(item)
            
        self.listView.setModel(self.model)
        self.listView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        
        #Message box
        self.msgBox = QMessageBox()
        self.loadingMsgBox = QMessageBox()
        
    def create_connections(self):
        """ create connections """
        self.selectButton.clicked.connect(self.select_all_dialog)
        self.unselectButton.clicked.connect(self.unselect_all_dialog)
        self.cameraCheckBox.stateChanged.connect(self.camera_setting_dialog)
        self.exportButton.clicked.connect(self.export_dialog)
        self.browseButton.clicked.connect(self.select_directory_dialog)
        self.browseButton_2.clicked.connect(self.select_directory_dialog_2)
        
        
##########################################################################################################
# SLOTS
##########################################################################################################
    def close_dialog(self):
        """ close this dialog """
        
        self.close()
        
    def select_all_dialog(self):
        """ select all geometry groups """
        
        for i in range(len(self.geo_grps)):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Checked)
            
    def unselect_all_dialog(self):
        """ unselect all geometry groups """
        
        for i in range(len(self.geo_grps)):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)
        
    def camera_setting_dialog(self):
        """ toggle show/hide camera setting """
        
        if self.cameraCheckBox.isChecked():
            self.show_camera_setting()
        else:
            self.hide_camera_setting()
        
    def hide_camera_setting(self):
        """ hide camera setting """
        
        self.customCamGroupBox.setVisible(False)
        
    def show_camera_setting(self):
        """ show camera setting """
        
        self.customCamGroupBox.setVisible(True)
        
        
    def set_default_setting(self):
        """ set default setting """
        
        #Initialize class 
        fm = FileManager()
        
        try:
            #Initialize Variables
            sceneFile = pm.sceneName()
            root = fm.get_root(sceneFile)
            project = fm.get_project(sceneFile)
            seqNum = fm.get_sequence_number(sceneFile)
            shotNum = fm.get_shot_number(sceneFile)
            cacheDir = fm.get_animation_cache_directory(root, project, seqNum, shotNum)
            abcPath = fm.get_animation_cache_file_path(cacheDir, shotNum)
            fileName = "{}.{}".format(fm.get_file_name(abcPath), fm.get_version(abcPath))
            
            start_frame = int(cmds.playbackOptions(q=1, animationStartTime=True))
            end_frame = int(cmds.playbackOptions(q=1, animationEndTime=True))
            cameraFileName = "ShotCamera"
            ext = "abc"
            
            #for geometry
            self.startSpinBox.setValue(start_frame)
            self.endSpinBox.setValue(end_frame)
            self.dirLineEdit.setText(cacheDir)
            self.fileNameLineEdit.setText(fileName)
            self.extLineEdit.setText(ext)
            
            #for camera
            self.startSpinBox_2.setValue(start_frame)
            self.endSpinBox_2.setValue(end_frame)
            self.dirLineEdit_2.setText(cacheDir)
            self.fileNameLineEdit_2.setText(cameraFileName)
            self.extLineEdit_2.setText(ext)
            
        except IndexError:
            self.msgBox.setText("The scene is not saved as right location. It needs to be saved at following location \n {root}/{project}/production/sequences/{sequence_num}/{shot_num}/animation/work/{<sequence>_animation.{version}.ma}")
            self.msgBox.exec_()
            
            
    def select_directory_dialog(self):
        """ allows user to select directory for geometry cache """
        
        selected_directory = QtGui.QFileDialog.getExistingDirectory()
        
        if selected_directory: self.dirLineEdit.setText(selected_directory)
        
    def select_directory_dialog_2(self):
        """ allows user to select directory for camera cache """
        
        selected_directory = QtGui.QFileDialog.getExistingDirectory()
        
        if selected_directory: self.dirLineEdit_2.setText(selected_directory)
        
        
    def export_dialog(self):
        """ export alembic cache """
        
        #get selected geometry groups
        self.selected_geo_grps = []
        for i in range(len(self.geo_grps)):
            item = self.model.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                self.selected_geo_grps.append(item.text())
        
        #check everything before exporting
        
        #wrong type of extension
        if self.extLineEdit.text() != "abc" or self.extLineEdit_2.text() != "abc":
            self.msgBox.setText("Please chance extenstion to 'abc'")
            self.msgBox.exec_()
            return
        
        if not self.assetManager.has_geo_grps:
            self.msgBox.setText("No geometry group is found")
            self.msgBox.exec_()
            
        
        self.msg = ""
        amount = 0
        
        performed = False
        #try:
        if len(self.selected_geo_grps) > 0:
            self.export_geometry_cache()
            performed = True
            
        if self.cameraCheckBox.isChecked():
            if not self.assetManager.has_shot_camera():
                self.msgBox.setText("No shot camera is found")
                self.msgBox.exec_()
                return 
            
            self.export_camera_cache()
            performed = True
            
        if performed:
            self.close_dialog()
            self.msg = "SUCCESSFUL! \n{}".format(self.msg)
        else:
            self.msg = "FAILED! \nPLEASE SELECT SOMETHING"
            
            
        self.msgBox.setText(self.msg)
        self.msgBox.exec_()
            
            
        #except Exception:
        #    self.msg = "Unexpected error"
        #    self.msgBox.setText(self.msg)
        #    self.msgBox.exec_()
        
        
    def export_geometry_cache(self):
        """ get values from GUI and export geometry cache """
        
        jsonBuilder = JsonBuilder()
        
        start_frame = self.startSpinBox.value()
        end_frame = self.endSpinBox.value()
        cache_dir = self.dirLineEdit.text()
        file_name = self.fileNameLineEdit.text()
        ext = self.extLineEdit.text()
        writeVisibility = False
        
        if self.writeVisCheckBox.isChecked(): writeVisibility = True
        
        setting = ExportAlembicSetting(start_frame, end_frame, writeVisibility)
        
        exportAlembic = ExportAlembic(setting)
        
        #set path where the alembic file is saved to
        export_to_path = os.path.join(cache_dir, "{}.{}".format(file_name, ext)).replace('\\', '/')
        print export_to_path
        
        #set path where the reference file is saved to
        write_to_path = os.path.join(cache_dir, "reference.json").replace('\\', '/')
        print write_to_path
        
        self.close_dialog()
        
        amount = 0
        
        pm.progressWindow(title='Exporting Cache', progress=amount, status='Initializing', isInterruptable=False)
        pm.pause(seconds=1)
        
        #TODO need to have "Please wait..." dialog appear while exporting. maybe research on threads? 
        while True:
            # Check if the dialog has been cancelled
            if pm.progressWindow(querry=True, isCancelled=True):
                break
            
            elapsedTime = pm.timerX()
            
            increment = 100/elapsedTime
            
            amount += increment
            
            #export alembic
            exportAlembic.do_export(self.selected_geo_grps, export_to_path)
            
            pm.pause(seconds=1)
            
            pm.progressWindow(edit=True, progress=amount, status="Exporting")
            
            print "Elapsed Time: {}".format(elapsedTime)
            break
        
        #create reference file and save as .json
        jsonBuilder.create_json_file(self.selected_geo_grps, export_to_path, write_to_path)
        
        pm.progressWindow(endProgress=1)
        
        self.msg = "Alembic file for geo_grps is at {} \n".format(export_to_path)
        
    def export_camera_cache(self):
        """ get values from GUI and export camera cache """
        
        #get camera geometry
        camera_geo = self.assetManager.get_shot_camera()
        start_frame = self.startSpinBox_2.value()
        end_frame = self.endSpinBox_2.value()
        cache_dir = self.dirLineEdit_2.text()
        file_name = self.fileNameLineEdit_2.text()
        ext = self.extLineEdit_2.text()
        writeVisibility = False
        
        if self.writeVisCheckBox_2.isChecked(): writeVisibility = True
        
        camera_setting = ExportAlembicSetting(start_frame, end_frame, writeVisibility)
        
        exportCamAlembic = ExportAlembic(camera_setting)
        
        #set path where the camera alembic file is saved to
        camera_export_to_path = os.path.join(cache_dir, "{}.{}".format(file_name, ext)).replace('\\', '/')
        
        #export camera alembic 
        exportCamAlembic.do_export(camera_geo, camera_export_to_path)
        
        self.msg = "{}Alembic file for ShotCamera is at {} \n".format(self.msg, camera_export_to_path)
        
if __name__ == "__main__":
    try:
        dialog.deleteLater()
    except:
        pass
    
    dialog = ExportAlembicUi()
    
    try:
        dialog.show()
    except:
        dialog.deleteLater()
        traceback.print_exc()
