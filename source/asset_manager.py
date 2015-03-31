import pymel.core as pm


class AssetManager():
    """ Handles with information such as dependant parents, root, geo_grp in assets """
    
    def __init__(self):
        print "from AssetManager"
        
    def get_root(self, child):
        """ obtain the root of the child 
        
        >>print get_root('shield_0:geo_grp')
        shield_0:all_grp
        
        :param child: any child 
        :type child: str.     
        :returns: str. -- return name of root node
        :raises
        
        """
        
        
        pm.select(child)
        
        childNode = pm.selected()[0]
        
        return childNode.root()
        
    def get_all_parents(self, child):
        """ Obtains the list of all parents of its child  
        
        >>print get_all_parents('woodenHill_0:geo_grp')
        ['woodenHill_0:geo_grp', 'woodenHill_0:root_ctrl', 'woodenhill_0:placement_ctrl', 'woodenHill_0:all_grp']
        
        :param child: any child
        :type child: list 
        :returns: list -- return list of all parents of its child  
        """
        
        #get root from the child
        root = self.get_root(child)
        
        #initialize variable 
        allParents = []
        
        #add child to list
        allParents.append(child)
        
        while (child != root):
            child = pm.listRelatives(child, allParents=True)[0]
            allParents.append(child)
             
        return allParents
    
    def get_geo_grps(self, namespaces):
        """ Obtains the list of geometries with name that contains 'geo_grp' from the list of namespaces
        
        >>print get_geometries(['skeleton_0', 'shield_0'])
        ['skeleton_0:model_0:geo_grp', 'shield_0:geo_grp']
        
        :param namespaces: list of namespaces
        :type namespaces: list
        :returns: return list -- list of all geometries that contains 'geo_grp'
        """        
        
        #initialize variable
        geoGrpsList = []
        
        for ns in namespaces:
            child_namespaces = pm.namespaceInfo(ns, listOnlyNamespaces=True)
            geo_grp = "{}:geo_grp".format(ns)
            if pm.uniqueObjExists(geo_grp):
                geoGrpsList.append(geo_grp)
            elif child_namespaces:
                geoGrpsList.extend(self.get_geo_grps(child_namespaces))
            else:
                break
     
        return geoGrpsList
        
        
    def has_geo_grps(self, namespaces):
        """ check if there is geo grps in scene 
        
        :returns: bool --- return true if there is
        """
        
        if self.get_geo_grps(namespaces) == 0: return False
        return True
        
    def build_dependancies(self, geo_grps):
        """Build dependancies input for alembic command

        >>print build_dependancies([skeleton_0:model_0:geo_grp, shield_0:geo_grp])
        -root |skeleton_0:all_grp|skeleton_0:model_0:geo_grp -root |shield_0:all_grp|shield_0:geo_grp

        :param geo_grps: selected geo_grp
        :type geo_grps: list 
        :returns: string -- return string of dependancies for each selected geo_grp
        """
        
        #initialize variable
        dependancies_string = ""
        
        for geo in geo_grps:
            dependancies_string = dependancies_string + "-root "
            parentList = self.get_all_parents(geo)
            for parent in reversed(parentList):
                if parent.startswith(":"): parent = parent[1:]
                dependancies_string = dependancies_string + "|{}".format(parent)
            dependancies_string = dependancies_string + " "

        return dependancies_string
        
        
        
    def get_shot_camera(self):
        """ Obtains shot camera 
        
        :returns: str. -- shot camera
        """
        
        return pm.listRelatives(pm.ls(type='camera')[0], allParents=True )
        
    def has_shot_camera(self):
        """check if there is a shot camera 
        
        :returns: bool --- return true if there is a shot camera
        """
        
        cameraObjs = pm.ls(type='camera')
        defaultCameraObjs = ['frontShape', 'leftShape', 'perspShape', 'sideShape', 'topShape']
        for obj in cameraObjs:
            if not obj in defaultCameraObjs:
                return True
                
        return False
        
    def add_alembic_attribute(self, geometry, abcFilePath):
        """ add custom/extra attribute to hold alembic file """
        
        pm.addAttr(geometry, longName="alembic", dt="string")
        
        alembicAttr = '{}.alembic'.format(geometry)
        
        pm.setAttr(alembicAttr, abcFilePath)
        
        
        
#############################TEST############################################################################
#am = AssetManager()
#print am.has_shot_camera()
        
   
#namespaces = pm.listNamespaces()
#am = AssetManager()
#selectedGeo = am.get_geo_grps(namespaces)
#print "all geo: {}".format(selectedGeo)       
