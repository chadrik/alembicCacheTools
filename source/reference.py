import pymel.core as pm
import maya.cmds as cmds


# FIXME: all of this can be replaced by utilities in pymel.system

class Reference(object):
    def __init__(self):
        self.ref = ref
    
    def unload(self):
        """ unload reference
         
        :param ref: any reference you want to unload 
        :type ref: string
        """
        
        cmds.file(unloadReference=self.ref)
        
        
    def load(self):
        """ load reference
         
        :param ref: any reference you want to load 
        :type ref: string
        """
        
        cmds.file(loadReference=self.ref)
        
        
    def cleanUp(self):
        """ clean up reference
        
        """
        
        cmds.file(cleanReference=self.ref)

    @classmethod
    def get_loaed_reference(cls):
        """ get loaded reference """
        
        references = cmds.ls(references=True)
        loaded=[]
        for ref in references:
            try:
                if cmds.referenceQuery(ref, isLoaded=True):
                    # TODO: cast to Reference?
                    loaded.append(ref)
            except:
                print "Warning: {} was not associated with a reference file".format(ref)
        
        return loaded            
    
    @classmethod
    def build_reference_command(self, nameSpace, sourcePath):
        """ build command in order to evaluate it in MEL when creating reference """
        
        command = 'file -r -type "mayaAscii" -gl -mergeNamespacesOnClash false -namespace "%s" -options "v=0;" "%s";'%(nameSpace, sourcePath)
        
        return command
        
    def create_reference(self, nameSpace, refCachePath):
        """ create Reference
        
        :param ref: any reference you want to create
        :type ref: string 
        """
        # FIXME: it is possible and preferable to use maya.cmds.file or
        # pm.createReference instead of evaluating a MEL string
        command = self.build_reference_command(nameSpace, refCachePath)
        
        print command
        
        pm.mel.eval(command)
        # TODO: return a Reference instance?
        
        
        
    



        