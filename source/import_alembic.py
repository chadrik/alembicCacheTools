import pymel.core as pm
import maya.cmds as cmds
import os
import re
import unicodedata
from asset_manager import AssetManager

class ImportAlembic():
    """
    ImportAlembic is class that import/bring alembic file into scene
    """
    def __init(self):
        pass
        
    def build_alembic_command(self, selectedItems, abcfilepath):
        """ build import alembic command to be able to evaluate it in MEL when importing """
        
        selected_item_string = ""
        
        for item in selectedItems:
            selected_item_string = selected_item_string + item + " "
            
        selected_item_string = self.strip_one_space(selected_item_string)
        
        command = 'AbcImport -mode import -fitTimeRange -connect "%s" -removeIfNoUpdate "%s";'%(selected_item_string, abcfilepath)
        
        return command
        
        
    def import_alembic(self, geo_grps, srtAbcPath):
        """ import alembic cache from the given source alembic cache path """
        
        command = self.build_alembic_command(geo_grps, srtAbcPath)
        
        print command
        
        pm.mel.eval(command)
        
        
    def import_shot_camera(self, srtAbcPath):
        """ import alembic cache for especially shot camera from the given source alembic shot camera cache path """
        
        command = 'AbcImport -mode import -fitTimeRange "{}"'.format(srtAbcPath)
        
        print command
        
        pm.mel.eval(command)
        
        
    def strip_one_space(self, s):
        """ strip one space for the given string as building import alembic command """
        
        if s.endswith(" "): s = s[:-1]
        
        if s.startswith(":"): s = s[1:]
        
        return s
        
        