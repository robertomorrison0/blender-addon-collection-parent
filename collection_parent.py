
bl_info = {
    "name": "Collection Parent",
    "author": "Roberto Morrison",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > SidePanel > Collection Parent",
    "description": "Addon to parent a collection by distance to another",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}
 
import bpy
from math import sqrt

items_parent = []
items_child = []
collections = []

def parents_created_callback(self, context):
    scene = context.scene
    print(str(parents_created) + " parents were created")
    return str(parents_created) + " parents were created"

def add_items_from_collection_callback(self, context):
    scene = context.scene
    collections.clear()
    for collection in bpy.data.collections:
        collections.append((collection.name, collection.name, ""))
    return collections

class MyProperties(bpy.types.PropertyGroup):
    float_distance : bpy.props.FloatProperty(name="Distance", soft_min=0,  soft_max=10, default=0.01, description="Maximum distance between parent and child")
    bool_keep_transform : bpy.props.BoolProperty(name="Keep Transform", default=True, description="child.matrix_parent_inverse = parent.matrix_world.inverted()")
    
    
    enum_parent_collection : bpy.props.EnumProperty(
        name= "Parent",
        description= "Choose Parent",
        items=add_items_from_collection_callback
    )
    
    enum_child_collection : bpy.props.EnumProperty(
        name= "Child",
        description= "Choose Child",
        items=add_items_from_collection_callback
    )
    

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

        def draw(self, context):
            self.layout.label(text=message)

        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
 
 
class parent(bpy.types.Operator):
    bl_idname = 'mesh.parent_execute'
    bl_label = 'Execute Parent'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Create parents (Parent collection -> Child Collection)"
    
    
    def execute(self, context):
         
        scene = context.scene
        items_parent.clear()
        items_child.clear()
        
        def find_min(list):
            temp = min(list)
            res = []
            for idx in range(0, len(list)):
                if temp == list[idx]:
                    res.append(idx)
            return res[0]

        if scene.my_tool.enum_child_collection == scene.my_tool.enum_parent_collection:
            ShowMessageBox("Parent and Child collection are the same. Please choose two distinct collections.", "Only one Collection chosen")
            return {"FINISHED"}

        for collection in bpy.data.collections:
            if collection.name == scene.my_tool.enum_child_collection:
                for obj in collection.all_objects:
                    items_child.append(obj)
            if collection.name == scene.my_tool.enum_parent_collection:
                for obj in collection.all_objects:
                    items_parent.append(obj)        
        
        print("------------------------------------------------------")
        print("child\t\t\tparent\t\t\tdistance")
        print("------------------------------------------------------")
        for  x in range( 0, len(items_child) ):
            a = items_child[x]
            distances = []
            obj_index = []
            for  y in range( 0, len(items_parent) ):
                b = items_parent[y]
                distance = abs(sqrt( (a.location[0] - b.location[0])**2 + (a.location[1] - b.location[1])**2 + (a.location[2] - b.location[2])**2))
                if distance <= scene.my_tool.float_distance:
                    distances.append(distance)
                    obj_index.append(y)
            if len(distances) > 0:
                
                b = items_parent[obj_index[find_min(distances)]]
                print(a.name + "\t\t" + b.name  + "\t\t" + str(min(distances)))
                a.parent = b
                if scene.my_tool.bool_keep_transform == True:
                    a.matrix_parent_inverse = b.matrix_world.inverted()

            
            
            
        return {"FINISHED"}

class unparent(bpy.types.Operator):
    bl_idname = 'mesh.unparent_execute'
    bl_label = 'Execute Parent'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove parents from child collection"
 
    def execute(self, context):

        scene = context.scene
        items_parent.clear()
        items_child.clear()
        for collection in bpy.data.collections:
            if collection.name == scene.my_tool.enum_child_collection:
                for obj in collection.all_objects:
                    obj.parent = None
                    
        return {"FINISHED"}
 
 
class panel(bpy.types.Panel):
    bl_idname = "panel.panel"
    bl_label = "Parent collection items by distance"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Collection Parent'
    
 
    def draw(self, context):
        scene = context.scene
        self.layout.prop(scene.my_tool, "enum_parent_collection")
        self.layout.prop(scene.my_tool, "enum_child_collection")
        self.layout.prop(scene.my_tool, "float_distance")
        self.layout.prop(scene.my_tool, "bool_keep_transform")
        self.layout.operator("mesh.unparent_execute", icon='MESH_CUBE', text="Clear Child Parents")
        self.layout.operator("mesh.parent_execute", icon='MESH_CUBE', text="Parent")
        
 
classes = [MyProperties, parent, unparent, panel]
 
def register() :
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type= MyProperties)
 
def unregister() :
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_tool
 
if __name__ == "__main__" :
    register()
    print(bpy.context.scene.my_tool.name)
    
    