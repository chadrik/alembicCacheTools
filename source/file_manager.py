import pymel.core as pm
import maya.cmds as cmds
import json
import os
import re
import unicodedata


PRODUCTION = "production"
SEQUENCES = "sequences"
ASSETS = "assets"
ANIMATION = "animation"
RIG = "rig"
PUBLISH = "publish"
CACHES = "caches"
DATA = "data"
RENDERLAYERS = "renderLayers"


def _join(*parts):
    return os.path.join(*parts).replace('\\','/')

class FileManager(object):
    """ Handle with all file system paths by defining a template for file paths with keys. 
    basically it's a config file with template defining a folder structure and naming convention. """
    
    def __init__(self, path):
        self.path = path
        
    def get_root(self):
        """ get root """
        
        return self.path.split('/')[0]
        
    def get_project(self):
        """ get project such as 10013_ucoolHeroesCharge """
        
        return self.path.split('/')[1]
        
    def get_sequence_number(self):
        """ get sequence number such as 0100 """
        
        return self.path.split('/')[4]
        
    def get_shot_number(self):
        """ get shot number such as 0100_0140 """
        
        return self.path.split('/')[5]
        
    def get_asset_type(self):
        """ get asset type such as character """
        
        return self.path.split('/')[4]
        
    def get_asset_name(self):
        """ get asset name such as skeleton """
        
        return self.path.split('/')[5]
        
    def get_directory(self):
        """get directory """
        
        return os.path.dirname(self.path)
    
    def get_tail(self):
        """ get tail """
        
        return os.path.split(self.path)[1]
        
    def get_file_name(self):
        """ get file asset name """
        
        return self.get_tail().split(".")[0]
        
    def get_version(self):
        """ get version such as 'v001' """
        
        return self.get_tail().split(".")[1]
        
    def get_extenstion(self):
        """ get extention such as 'ma', 'abc' """
        
        return self.get_tail().split(".")[2]
    
    @classmethod
    def get_data_directory(cls, root, project):
        """ get direcory for data folder 
        {root}/{project}/production/sequences/data
        """
        
        return _join(root, project, PRODUCTION, SEQUENCES, DATA)
    
    @classmethod
    def get_render_layers_directory(cls, root, project):
        """ get directory for render layers
        {root}/{project}/production/sequences/data/renderLayers
        """
        
        return _join(cls.get_data_directory(root, project), RENDERLAYERS)
    
    @classmethod
    def get_export_render_layers_file_path(cls, root, project, shotNumber, prefix):
        """ get file path for exporting render layers
        {root}/{project}/production/sequences/data/renderLayers/{shotNumber}/{prefix}
        """
        
        dir = cls.get_render_layers_directory(root, project)
        
        dir = os.path.join(dir, shotNumber).replace('\\','/')
        
        if os.path.isdir(dir):
            dir = os.path.join(dir, prefix).replace('\\','/')
            return dir
        else:
            return None
    
    @classmethod
    def get_import_render_layers_file_path(cls, root, project, shotNumber):
        """ get file path for importing render layers
        {root}/{project}/production/sequences/data/renderLayers/{shotNumber}
        """
        dir = cls.get_render_layers_directory(root, project)
            
        dir = os.path.join(dir, shotNumber).replace('\\','/')
        
        if os.path.isdir(dir): return dir
        else: return None
    
    @classmethod
    def get_animation_cache_directory(cls, root, project, seqNumber, shotNumber):
        """ get cache directory for animation
        {root}/{project}/production/sequences/{sequence_num}/{shot_num}/animation/publish/caches/
        """

        dir = _join(root, project, "production", "sequences", seqNumber,
                    shotNumber, "animation", "publish", "caches")
        
        if os.path.exists(dir):
            return dir
        else:
            return None
        
    @classmethod
    def get_shader_cache_directory(cls, root, project, assetType, assetName):
        """ get cache directory for shader
        {root}/{project}/production/assets/{asset_type}/{asset_name}/rig/publish/caches/
        """
        
        # FIXME: use technique from get_data_directory and get_animation_cache_directory
        dir = "{}/".format(root)
        dir = os.path.join(dir, project).replace('\\','/')
        dir = os.path.join(dir, "production").replace('\\','/')
        dir = os.path.join(dir, "assets").replace('\\','/')
        dir = os.path.join(dir, assetType).replace('\\','/')
        dir = os.path.join(dir, assetName).replace('\\','/')
        dir = os.path.join(dir, "rig").replace('\\','/')
        dir = os.path.join(dir, "publish").replace('\\','/')
        dir = os.path.join(dir, "caches").replace('\\','/')
        
        if os.path.exists(dir): return dir
        else: return None
        
        
        
    def get_json_write_to_path(self, shotNumber):
        """ make file path in order to save json file """
        
        return _join(self.path, "{}_reference.json".format(shotNumber))
        
        
    def get_animation_cache_file_path(self, shotNumber):
        """
        get file path when exporting alembic path following the file structure below
        directory should be like {root}/{project}/production/sequences/{sequence_num}/{shot_num}/animation/publish/caches/
        file name will be {sequence_animation}.{latest_version}.abc
        """
        
        return os.path.join(self.path, self.get_animation_cache_file(shotNumber)).replace('\\','/')
        
    def get_animation_cache_file(self, shotNumber):
        """
        get file when exporting alembic path following the file structure below
        directory should be like {root}/{project}/production/sequences/{sequence_num}/{shot_num}/animation/publish/caches/
        file name will be {sequence_animation}.{latest_version}.abc
        """
        
        #get latest file from the directory
        latestVerFile = self.get_latest_version_file("abc")
        
        #if no cache is found in the directory, make new one
        if not latestVerFile:
            return _join(self.path, "{}_animation.v001.abc".format(shotNumber))
        
        #increase version of the file
        return self.increase_version(latestVerFile)
        
        
        
    def get_camera_export_cache_file_path(self):
        """
        get file path when exporting alembic path following the file structure below
        directory should be like {root}/{project}/production/sequences/{sequence_num}/{shot_num}/animation/publish/caches/
        file name will be ShotCamera.abc
        """
        
        return os.path.join(self.path, "{}.{}".format("ShotCamera", "abc")).replace('\\','/')
        
        
    def has_shot_camera(self):
        """
        Return True if there is shot camera cache in the given directory
        Return False if no shot camera is found
        file name for shot camera cache must be "ShotCamera.abc" with case sensitivity in order to find it
        """
        
        for file in os.listdir(self.path):
            if len(file.split(".")) == 2:
                filename, extension = file.split(".")
                if filename == "ShotCamera" and extension == "abc":
                    return True             
        return False
        
        
    def get_camera_import_cache_file_path(self):
        """ 
        get file path when importing shot camera cache
        directory should be like {root}/{project}/production/sequences/{sequence_num}/{shot_num}/animation/publish/caches/
        file name for shot camera must be "ShotCamera.abc" with case sensitivity in order to find it
        """
        
        for file in os.listdir(self.path):
            if len(file.split(".")) == 2:
                filename, extension = file.split(".")
                if filename == "ShotCamera" and extension == "abc":
                    return os.path.join(self.path, file).replace('\\', '/') 
        return None
        
    def get_shader_cache_file_path(self):
        """
        get file path for shader cache following the file structure below
        directory should be like {root}/{project}/production/assets/{asset_type}/{asset_name}/rig/publish/caches/
        file name will be {asset_name}.{latest_version}.ma 
        """
        
        #get latest file from the directory
        latestVerFile = self.get_latest_version_file("ma")
        
        return os.path.join(self.path, latestVerFile).replace('\\','/')
        
    def get_reference_file_path(self, root, project, seqNum, shotNum):
        """ 
        build directory with given root, project, sequence number, and shot number and return the path with json.file if exists
        the final path should be like 
        {root}/{project}/production/sequences/{sequence_num}/{shot_num}/animation/publish/caches/reference.json
        """
        # FIXME: use technique from get_data_directory and get_animation_cache_directory
        dir = os.path.join(root, project)
        dir = os.path.join(dir, PRODUCTION)
        dir = os.path.join(dir, SEQUENCES)
        dir = os.path.join(dir, seqNum)
        dir = os.path.join(dir, shotNum)
        dir = os.path.join(dir, ANIMATION)
        dir = os.path.join(dir, PUBLISH)
        dir = os.path.join(dir, CACHES)
        
        if os.path.isdir(dir):
            files = os.listdir(dir)
            for file in files:
                if file.endswith('.json'):
                    return os.path.join(dir, file)
                    
        return None 
        
        
    def has_cache_file(self, file_extension):
        """ return true if there cache file corresponding with file extension  """
        
        for dir in os.listdir(self.path):
            if len(dir.split(".")) == 3: 
                filename, version, extension = dir.split(".")
                if extension == file_extension:
                    return True
        
        return False
        
        
    def get_latest_version_file(self, file_extension):
        """ Finds the latest version file for the given file name. """
        
        #initialize variables
        preVersion = 0
        latestVersion = 0
        latestVersionFilename = "" 
        
        #error handle for directory does not exist
        if not os.path.isdir(self.path):
            return None
        
        #error handle for empty in directory 
        if not os.listdir(self.path):
            return None
        
        for dir in os.listdir(self.path):
            if len(dir.split(".")) == 3: 
                fileName, version, extension = dir.split(".")
                if extension == file_extension:
                    currVersion = int(version.split("v")[1])
                    if currVersion >= preVersion:
                        latestVersion = currVersion
                        latestVersionFilename = fileName
                        
                        
        return "{}.v{:03}.{}".format(latestVersionFilename, latestVersion, file_extension)
        
        
    def increase_version(self):
        """ Increase version of the current file name """
        
        file_name, version, ext = self.path.split(".") 
        version_number = int(version.split("v")[1])
        version_number = version_number + 1
        return "{}.v{:03}.{}".format(file_name, version_number, ext)
         
         
         
###############################################TEST#####################################################################
#am = AssetManager()
#fm = FileManager()
#geo_grps = am.get_geo_grps(pm.listNamespaces())
#CACHE = "C:/SampleProject/production/sequences/0100/0100_0100/animation/publish/caches/0100_0100_animation.v006.abc"
#root = fm.get_root(CACHE)
#project = fm.get_project(CACHE)
#shotNum = fm.get_shot_number(CACHE)
#print fm.get_data_directory(root, project)