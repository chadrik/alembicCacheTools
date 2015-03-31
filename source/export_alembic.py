import pymel.core as pm
import maya.cmds as cmds
import os
import re
import unicodedata
from asset_manager import AssetManager
        
        
class ExportAlembic(object):
    """
    ExportAlembic is class that automatically selects all geo_grp and export them as alembic file
    """
    def __init__(self, start, end, writeVisibility):
        print "From ExportAlembic"
        self.assetManager = AssetManager()
        self.start = start
        self.end = end
        self.writeVisibility = writeVisibility
        
    def build_alembic_command(self, geo_grps, abcFilePath):
        """    
        build MEL command for export alembic
        """
        start_frame = self.start
    
        end_frame = self.end
        
        if self.writeVisibility: writeVisibility = " -writeVisibility"
        else: writeVisibility = ""
        
        depList = self.assetManager.build_dependancies(geo_grps)
        
        
        command = 'AbcExport -j "-frameRange {} {} -ro -uvWrite -worldSpace{} {}-file {}"'.format(start_frame, end_frame, writeVisibility, depList, abcFilePath)

        return command
        
    def do_export(self, geo_grps, abcFilePath):
        """
        Excecute export command
        """
        #abcFilePath
        command = self.build_alembic_command(geo_grps, abcFilePath)
        
        pm.select(geo_grps)
        
        print command
        pm.mel.eval(command)
        