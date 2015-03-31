import pymel.core as pm
import maya.cmds as cmds




class Reference():
    def __init__(self):
        pass
    
    def unload(self, ref):
        """ unload reference
         
        :param ref: any reference you want to unload 
        :type ref: string
        """
        
        cmds.file(unloadReference=ref)
        
        
    def load(self, ref):
        """ load reference
         
        :param ref: any reference you want to load 
        :type ref: string
        """
        
        cmds.file(loadReference=ref)
        
        
    def cleanUp(self, ref):
        """ clean up reference
        
        """
        
        cmds.file(cleanReference=ref)

        
    def get_loaed_reference(self):
        """ get loaded reference """
        
        references = cmds.ls(references=True)
        loaded=[]
        for ref in references:
            try:
                if cmds.referenceQuery(ref, isLoaded=True):
                    loaded.append(ref)
            except:
                print "Warning: {} was not associated with a reference file".format(ref)
        
        return loaded            
        
    def build_reference_command(self, nameSpace, sourcePath):
        """ build command in order to evaluate it in MEL when creating reference """
        
        command = 'file -r -type "mayaAscii" -gl -mergeNamespacesOnClash false -namespace "%s" -options "v=0;" "%s";'%(nameSpace, sourcePath)
        
        return command
        
    def create_reference(self, nameSpace, refCachePath):
        """ create Reference
        
        :param ref: any reference you want to create
        :type ref: string 
        """
        
        command = self.build_reference_command(nameSpace, refCachePath)
        
        print command
        
        pm.mel.eval(command)
        
        
        
        
    



        