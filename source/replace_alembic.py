import pymel.core as pm
import maya.cmds as cmds
import os
import sys

from reference import Reference
from file_manager import FileManager

from asset_manager import AssetManager

#from render_layer import RenderLayer
sys.path.append("O:/Code/Pipeline/scripts/render_layer")
from render_layer import RenderLayer

PREFIX = "render"

class ReplaceAlembic():
    
    
    def __init__(self):
        self.reference = Reference()
        
    def make_render_layer_folder(self, root, project, shotNum):
        """ make new folder in order to store render layers
        
        """
        
        #initialize class
        fm = FileManager()
        print root
        print project
        print shotNum
        
        #get render layers directory {root}/{project}/production/sequences/data/renderLayers
        render_layers_dir = fm.get_render_layers_directory(root, project)
        
        #if render layers directory does not exist, create folder named 'renderLayers'
        if not os.path.isdir(render_layers_dir):
            data_dir = fm.get_data_directory(root, project)
            
            #if data directory does not exist, create folder named 'data'
            if not os.path.isdir(data_dir): os.makedirs(data_dir)
            
            os.makedirs(render_layers_dir)
            
        
        newPath = os.path.join(render_layers_dir, shotNum).replace('\\','/')
        
        
        #create folder named after shot number {root}/{project}/production/sequences/data/renderLayers/{shotNum}
        if not os.path.exists(newPath): os.makedirs(newPath)
        
        
        
    def replace_cache(self, selectedItems, abcFilePath, hasRenderLayers):
        """ replace alembic cache with the given cache filePath
         
        :param selectedItems:  
        :type selectedItems: list
        :parm abcFilePath: the file structure should be 
        {root}/{project}/production/sequences/{sequence_num}/{shot_num}/animation/publish/caches/{sequence_animation}.{latest_version}.abc
        :type abcFilePath: string
        :parm hasRenderlayers:
        :type hasRenderLayers: bool 
        """
        if not os.path.exists(abcFilePath):
            return None
            
        if len(selectedItems) == 0:
            return None
        
        #O:\10013_ucoolHeroesCharge\production\sequences\data\renderLayers
        #initialize class
        fm = FileManager()
        
        #initialize variable
        amount = 0
        root = fm.get_root(abcFilePath)
        project = fm.get_project(abcFilePath)
        shotNum = fm.get_shot_number(abcFilePath)
        
        #decide the amount of increment
        if hasRenderLayers:
            rl = RenderLayer()
            increment =  100 / ((len(selectedItems) * 3) + 4)
        else:
            increment = 100 / ((len(selectedItems) * 3) + 1)
        
        pm.progressWindow(title='Replacing Cache', progress=amount, status='Initializing', isInterruptable=False)
        pm.pause(seconds=1)
        
        #TODO: set interrupt for progress bar as True
        
        while True:
            # Check if the dialog has been cancelled
            if pm.progressWindow(querry=True, isCancelled=True):
                break
            
            
            if hasRenderLayers:
                #make folder to store render layers
                self.make_render_layer_folder(root, project, shotNum)
                
                #export render layers
                amount += increment
                self.setLabel("Exporting Render Layers", amount)
                filePathPrefix = fm.get_export_render_layers_file_path(root, project, shotNum, PREFIX)
                rl.exportAllRenderLayers(filePathPrefix)
                
                #delete render layers
                amount += increment
                self.setLabel("Deleting Render Layers", amount)
                rl.deleteAllRenderLayers()
            
            loaded_references = self.reference.get_loaed_reference()
                
            for reference in loaded_references:
                amount += increment
                self.setLabel("Unloading {}".format(reference), amount)
                self.reference.unload(reference)
                amount += increment
                self.setLabel("Cleaning up {}".format(reference), amount)
                self.reference.cleanUp(reference)
                amount += increment
                self.setLabel("Loading {}".format(reference), amount)
                self.reference.load(reference)
            
            amount += increment
            self.setLabel("Importing cache", amount)
            self.import_cache(selectedItems, abcFilePath)
            
            #import render layers
            if hasRenderLayers:
                amount += increment
                self.setLabel("Importing Render Layers", amount)
                filePath = fm.get_import_render_layers_file_path(root, project, shotNum)
                rl.importAllRenderLayers(filePath)
            
            break
            
            
        pm.progressWindow(endProgress=1)
        
    def setLabel(self, msg, amount):
        """ update label in progress bar if something is changed """
        
        pm.pause(seconds=1)
        
        return pm.progressWindow(edit=True, progress=amount, status=("{}: {}%".format(msg, amount)))
        
    def import_cache(self, selectedItems, abcFilePath):
        """ 
         import alembic cache
        :param selectedItems: selected geo_grps 
        :type ref: string
        """
        
        command = self.build_import_command(selectedItems, abcFilePath)
        
        print command
        
        pm.mel.eval(command)
        
        
    def build_import_command(self, selectedItems, abcFilePath):
        """ build command for importing alembic cache in order to execute in MEL """
        
        #initialize variable 
        selected_item_string =""
        
        for item in selectedItems:
            selected_item_string = "{} {}".format(selected_item_string, self.strip_one_space(item))
        
        #selected_item_string = self.strip_one_space(selected_item_string)    
        command = 'AbcImport -mode import -fitTimeRange -connect "{}" -removeIfNoUpdate "{}";'.format(selected_item_string[1:], abcFilePath)
        
        return command
        
        
    def strip_one_space(self, s):
        
        if s.endswith(" "): s = s[:-1]
        
        if s.startswith(":"): s = s[1:]
        
        return s
        

##############################################TEST###########################################################################################
#ra = ReplaceAlembic()
#am = AssetManager()
#geo_grps = am.get_geo_grps(pm.listNamespaces())
#print geo_grps
#CACHE = "C:/SampleProject/production/sequences/0100/0100_0100/animation/publish/caches/0100_0100_animation.v007.abc"
#print CACHE
#print len(geo_grps)
#ra.replace_cache(geo_grps, CACHE, True)



