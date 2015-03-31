import json
import pymel.core as pm
from asset_manager import AssetManager
from file_manager import FileManager

class JsonBuilder():
    """ Plays the role of building, writing, and reading data. """
    
    def __init__(self):
        print "from json"
        pass
        
    def read(self, file_path):
        """ read json file and recieve data """
        
        with open(file_path.replace('\\', '/'), 'rb') as fh:
            data = json.load(fh)
        
        return data
        
    def write(self, file_path, data):
        """ write data to json file. 
        
        :param file_path: file path to where will be written
        :type file_path: str. 
        :param data: data which will be written in json file
        :type data: list
        
        """
        print data 
        with open(file_path.replace('\\', '/'), 'wb') as fh:
            fh.write(json.dumps(data, ensure_ascii=True, indent=2))
        

    def create_json_file(self, selectedItems, abcFilePath, writeToPath):
        """ get data from geo_grps such as shader cache file path, animation cache file path, namespace

        :param selectedItems: selected assets which ends with geo_grp
        :type selectedItems: list

        """
        #Initialize class
        fm = FileManager()
        
        wholeData = []
        
        #writeToPath = self.sceneFile.build_json_write_to_path()

        for item in selectedItems:
            shadeCachePath = ""
            itemPath = pm.referenceQuery(item, filename=True)
            itemNodes = pm.referenceQuery(item, nodes=True, showNamespace=True)
            nameSpace = itemNodes[0].split(":")[0]
            
            root = fm.get_root(itemPath)
            project = fm.get_project(itemPath)
            assetType = fm.get_asset_type(itemPath)
            assetName = fm.get_asset_name(itemPath)
            
            cacheDir = fm.get_shader_cache_directory(root, project, assetType, assetName)
            
            if fm.has_cache_file(cacheDir, "ma"):
                shadeCachePath = fm.get_shader_cache_file_path(cacheDir)
            else:
                shadeCachePath = "No rig cache is found in {}".format(cacheDir)
                print "WARNING: {}".format(shadeCachePath)
            print shadeCachePath
            data = self.build_data(nameSpace, shadeCachePath, abcFilePath)
            wholeData.append(data)  

        referenceData = {"reference": wholeData}

        print writeToPath
       
        self.write(writeToPath, referenceData)
        
        
    def build_data(self, nameSpace, shaderCachePath, animationCachePath):
        """ build data """

        data = { "name_space": nameSpace, 
            "shader_cache_file_path": shaderCachePath, 
            "animation_cache_file_path": animationCachePath}

        return data
        
#jb = JsonBuilder()
#am = AssetManager()
#selectedGeo = am.get_geo_grps(pm.listNamespaces())
#jb.create_json_file(selectedGeo, ABCFILE, WRITEPATH)
