# ##### BEGIN GPL LICENSE BLOCK #####
#
#  fishsim.py  -- a script to apply a fish swimming simulation to an armature
#  by Ian Huish (nerk)
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# version comment: V4.02.0 - Goldfish Version - Blender 4.20 Extensions

bl_info = {
    "name": "FishSim",
    "author": "Ian Huish (nerk)",
    "version": (4, 2, 0),
    "blender": (4, 2, 0),
    "location": "Toolshelf>FishSim",
    "description": "Apply fish swimming action to a Rigify Shark armature",
    "warning": "",
    "wiki_url": "http://github.com/nerk987/FishSim",
    "tracker_url": "http://github.com/nerk987/FishSim/issues",
    "category": "Animation"}
    

if "bpy" in locals():
    import imp
    imp.reload(FishSim)
    imp.reload(metarig_menu)
    # print("Reloaded multifiles")
else:
    from . import FishSim
    # print("Imported multifiles")

import bpy
import mathutils,  math, os
import addon_utils
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, StringProperty
from random import random
from bpy.types import Operator, Panel, Menu
from bl_operators.presets import AddPresetBase
# import shutil

# print(sys.modules[bpy.types.DATA_PT_rigify_buttons.__module__].__file__)    

def add_preset_files():
    presets   = bpy.utils.user_resource('SCRIPTS', path="presets")
    mypresets = os.path.join(presets, "operator\\fishsim")
    if not os.path.exists(mypresets):
        os.makedirs(mypresets)    
        # print("Presets dir added:", mypresets)
    # mypath = os.path.join(mypresets, "myfile.xxx")


class FSimMainProps(bpy.types.PropertyGroup):
    fsim_targetrig : StringProperty(name="Name of the target rig", default="")  
    fsim_start_frame : IntProperty(name="Simulation Start Frame", default=1)  
    fsim_end_frame : IntProperty(name="Simulation End Frame", default=250)  
    fsim_maxnum : IntProperty(name="Maximum number of copies", default=250)  
    fsim_copyrigs : BoolProperty(name="Distribute multiple copies of the rig", default=False)  
    fsim_copymesh : BoolProperty(name="Distribute multiple copies of meshes", default=False)  
    fsim_multisim : BoolProperty(name="Simulate the multiple rigs", default=False)  
    fsim_startangle : FloatProperty(name="Angle to Target", default=0.0)
    



    # fout     = open(mypath)
    


# bpy.types.Scene.FSimMainProps.fsim_start_frame = IntProperty(name="Simulation Start Frame", default=1, update=updateStartFrame)  
# bpy.types.Scene.FSimMainProps.fsim_end_frame = IntProperty(name="Simulation End Frame", default=250, update=updateEndFrame)  
# bpy.types.Scene.FSimMainProps.fsim_maxnum = IntProperty(name="Maximum number of copies", default=250)  
# bpy.types.Scene.FSimMainProps.fsim_copyrigs = BoolProperty(name="Distribute multiple copies of the rig", default=False)  
# bpy.types.Scene.FSimMainProps.fsim_copymesh = BoolProperty(name="Distribute multiple copies of meshes", default=False)  
# bpy.types.Scene.FSimMainProps.fsim_multisim = BoolProperty(name="Simulate the multiple rigs", default=False)  
# bpy.types.Scene.FSimMainProps.fsim_startangle = FloatProperty(name="Angle to Target", default=0.0)  


class ARMATURE_OT_FSim_Add(bpy.types.Operator):
    """Add a target object for the simulated fish to follow"""
    bl_label = "Add a target"
    bl_idname = "armature.fsim_add"
    bl_options = {'REGISTER', 'UNDO'}
    


    def execute(self, context):
        #Get the object
        TargetRig = context.active_object
        for mod in addon_utils.modules():
            if mod.bl_info.get("name") == "FishSim":
                print("Path: ", os.path.dirname(mod.__file__) + os.sep + "presets")
        
        if TargetRig.type != "ARMATURE":
            print("Not an Armature", context.object.type)
            return {'CANCELLED'}
       
        TargetRoot = TargetRig.pose.bones.get("root")
        if (TargetRoot is None):
            print("No root bone in Armature")
            self.report({'ERROR'}, "No root bone in Armature - this addon needs a Rigify rig generated from a Shark Metarig")
            return {'CANCELLED'}

        TargetRoot["TargetProxy"] = TargetRig.name + '_proxy'
        #Add the proxy object
        bpy.ops.mesh.primitive_cube_add()
        bound_box = bpy.context.active_object
        #copy transforms
        bound_box.dimensions = TargetRig.dimensions
        bpy.ops.object.transform_apply(scale=True)
        bound_box.location = TargetRig.location
        bound_box.rotation_euler = TargetRig.rotation_euler
        bound_box.name = TargetRoot["TargetProxy"]
        bound_box.display_type = 'WIRE'
        bound_box.hide_render = True
        bound_box.visible_camera = False
        bound_box.visible_diffuse = False
        bound_box.visible_shadow = False
        bound_box["FSim"] = "FSim_"+TargetRig.name[:3]
        # if "FSim" in bound_box:
            # print("FSim Found")
        # bound_box.select = False
        #context.active_pose_bone = TargetRoot
        
        return {'FINISHED'}



#UI Panels
class AMATURE_MT_fsim_presets(Menu):
    bl_label = "FishSim Presets"
#    for mod in addon_utils.modules():
#        if mod.bl_info.get("name") == "FishSim":
#            preset_subdir = os.path.dirname(mod.__file__) + os.sep + "presets"
    preset_subdir = "../../extensions/user_default/FishSim/presets"
    preset_operator = "script.execute_preset"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'CYCLES_RENDER', 'BLENDER_GAME'}
    draw = Menu.draw_preset
    
class AddPresetFSim(AddPresetBase, Operator):
    '''Add a Object Draw Preset'''
    bl_idname = "armature.addpresetfsim"
    bl_label = "Add FSim Draw Preset"
    preset_menu = "AMATURE_MT_fsim_presets"

    # variable used for all preset values
    preset_defines = [
        "pFS = bpy.context.scene.FSimProps"
        ]

    # properties to store in the preset
    preset_values = [
        "pFS.pMass",
        "pFS.pDrag",
        "pFS.pPower",
        "pFS.pMaxFreq",
        "pFS.pMaxTailAngle",
        "pFS.pAngularDrag",
        "pFS.pMaxSteeringAngle",
        "pFS.pTurnAssist",
        "pFS.pLeanIntoTurn",
        "pFS.pEffortGain",
        "pFS.pEffortIntegral",
        "pFS.pEffortRamp",
        "pFS.pMaxTailFinAngle",
        "pFS.pTailFinPhase",
        "pFS.pTailFinStiffness",
        "pFS.pTailFinStubRatio",
        "pFS.pMaxSideFinAngle",
        "pFS.pSideFinPhase",
        # "pFS.pSideFinStiffness",
        "pFS.pChestRatio",
        "pFS.pChestRaise",
        "pFS.pMaxVerticalAngle",
        "pFS.pRandom",
        "pFS.pMaxPecFreq",
        "pFS.pMaxPecAngle",
        "pFS.pPecPhase",
        "pFS.pPecStubRatio",
        "pFS.pPecStiffness",
        "pFS.pPecEffortGain",
        "pFS.pPecTurnAssist",
        "pFS.pHTransTime",
        "pFS.pSTransTime",
        "pFS.pPecOffset",
        "pFS.pHoverDist",
        "pFS.pHoverTailFrc",
        "pFS.pHoverMaxForce",
        "pFS.pHoverDerate",
        "pFS.pHoverTilt",
        "pFS.pPecDuration",
        "pFS.pPecDuty",
        "pFS.pHoverTwitch",
        "pFS.pHoverTwitchTime",
        "pFS.pPecSynch"
        "pFS.pPecTransition"
        ]

    # where to store the preset
#    preset_subdir = "../FishSim/presets"
    preset_subdir = "../../extensions/user_default/FishSim/presets"
#    for mod in addon_utils.modules():
#        if mod.bl_info.get("name") == "FishSim":
#            preset_subdir = os.path.dirname(mod.__file__) + os.sep + "presets"
    

class ARMATURE_OT_FSim_Run(bpy.types.Operator):
    """Simulate and add keyframes for the armature to make it swim towards the target"""
    bl_label = "Copy Models"
    bl_idname = "armature.fsim_run"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    
    # add_preset_files()
    
    root = None

    

    def CopyChildren(self, context, src_obj, new_obj):
        for childObj in src_obj.children:
            # print("Copying child: ", childObj.name)
            new_child = childObj.copy()
            new_child.data = childObj.data.copy()
            new_child.animation_data_clear()
            new_child.location = childObj.location - src_obj.location
            new_child.parent = new_obj
            new_child.matrix_parent_inverse = childObj.matrix_parent_inverse
            context.collection.objects.link(new_child)
            new_child.select_set(True)
            for mod in new_child.modifiers:
                if mod.type == "ARMATURE":
                    mod.object = new_obj

    
    def CopyRigs(self, context):
        # print("Populate")
        
        scene = context.scene
        src_obj = context.object
        if src_obj.type != 'ARMATURE':
            return {'CANCELLED'}
        src_obj.select_set(True)
        
        #make a list of armatures
        armatures = {}
        for obj in scene.objects:
            if obj.type == "ARMATURE" and obj.name[:3] == src_obj.name[:3]:
                root = obj.pose.bones.get("root")
                if root != None:
                    if 'TargetProxy' in root:
                        proxyName = root['TargetProxy']
                        if len(proxyName) > 1:
                            armatures[proxyName] = obj.name
        
        #for each target...
        obj_count = 0
        for obj in scene.objects:
            if "FSim" in obj and (obj["FSim"][-3:] == src_obj.name[:3]):
                #Limit the maximum copy number
                if obj_count >= scene.FSimMainProps.fsim_maxnum:
                    return  {'FINISHED'}
                obj_count += 1
                
                #Go back to the first frame to make sure the rigs are placed correctly
                scene.frame_set(scene.FSimMainProps.fsim_start_frame)
                # scene.update()
                
                #if a rig hasn't already been paired with this target, and it's the right target type for this rig, then add a duplicated rig at this location if 'CopyRigs' is selected
                if (obj.name not in armatures) and (obj["FSim"][-3:] == src_obj.name[:3]):
                    # print("time to duplicate")

                    if scene.FSimMainProps.fsim_copyrigs:
                        #If there is not already a matching armature, duplicate the template and update the link field
                        new_obj = src_obj.copy()
                        new_obj.data = src_obj.data.copy()
                        # new_obj.animation_data_clear()
                        context.collection.objects.link(new_obj)
                        
                        #Unlink from original action
                        new_obj.animation_data.action = None
                        
                        #2.8 Issue Workout how to update drivers
                        #Update drivers with new rig id
                        for dr in new_obj.data.animation_data.drivers:                            
                            for v1 in dr.driver.variables:
                                # print("ID_name: ", v1.targets[0].id.name)
                                # print("obj_name:", src_obj.name)
                                if (v1.targets[0].id_type == 'OBJECT') and (v1.targets[0].id.name == src_obj.name):
                                    # print("Update_p", v1.targets[0].id)
                                    v1.targets[0].id = new_obj
                                    # print("Update", v1.targets[0].id)
                                
                        new_obj.location = obj.matrix_world.to_translation()
                        new_obj.rotation_euler = obj.rotation_euler
                        new_obj.rotation_euler.z += math.radians(scene.FSimMainProps.fsim_startangle)
                        new_root = new_obj.pose.bones.get('root')
                        new_root['TargetProxy'] = obj.name
                        new_root.scale = (new_root.scale.x * obj.scale.x, new_root.scale.y * obj.scale.y, new_root.scale.z * obj.scale.z)
                        context.view_layer.objects.active = new_obj
                        new_obj.select_set(True)
                        src_obj.select_set(False)
                        
                        #if 'CopyMesh' is selected duplicate the dependents and re-link
                        if scene.FSimMainProps.fsim_copymesh:
                            self.CopyChildren(context, src_obj, new_obj)

                #If there's already a matching rig, then just update it
                elif obj["FSim"][-3:] == src_obj.name[:3]:
                    # print("matching armature", armatures[obj.name])
                    TargRig = scene.objects.get(armatures[obj.name])
                    if TargRig is not None:
                        #reposition if required
                        if scene.FSimMainProps.fsim_copyrigs:
                            # TargRig.animation_data_clear()
                            TargRig.location = obj.matrix_world.to_translation()
                            TargRig.rotation_euler = obj.rotation_euler
                            TargRig.rotation_euler.z += math.radians(scene.FSimMainProps.fsim_startangle)
                            TargRig.keyframe_insert(data_path='rotation_euler',  frame=(scene.FSimMainProps.fsim_start_frame))
                            TargRig.keyframe_insert(data_path='location',  frame=(scene.FSimMainProps.fsim_start_frame))
                        
                        #if no children, and the 'copymesh' flag set, then copy the associated meshes
                        if scene.FSimMainProps.fsim_copymesh and len(TargRig.children) < 1:
                            self.CopyChildren(context, src_obj, TargRig)
                        
                        #Leave the just generated objects selected
                        # scene.objects.active = TargRig
                        TargRig.select_set(True)
                        src_obj.select_set(False)
                        for childObj in TargRig.children:
                            childObj.select_set(True)
                        for childObj in src_obj.children:
                            childObj.select_set(True)

                        # #Animate
                        # if scene.FSimMainProps.fsim_multisim and TargRig.name != src_obj.name:
                            # # self.BoneMovement(TargRig, scene.FSimMainProps.fsim_start_frame, scene.FSimMainProps.fsim_end_frame, context)
                            # bpy.ops.armature.fsimulate()
                
            


        
    def execute(self, context):
        #Get the object
        TargetRig = context.object
        scene = context.scene
        scene.FSimMainProps.fsim_targetrig = TargetRig.name
        scene = context.scene
        if TargetRig.type != "ARMATURE":
            print("Not an Armature", context.object.type)
            return  {'FINISHED'}
       
        # print("Call test")
        # bpy.ops.armature.fsim_test()
        
        if scene.FSimMainProps.fsim_copyrigs or scene.FSimMainProps.fsim_copymesh:
            self.CopyRigs(context)
        # else:
            # # self.BoneMovement(TargetRig, scene.FSimMainProps.fsim_start_frame, scene.FSimMainProps.fsim_end_frame, context)   
            # bpy.ops.armature.fsimulate()
        
        return {'FINISHED'}

        
    

class ARMATURE_PT_FSim(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "FishSim"   
    bl_idname = "armature.fsim"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FishSim"
    #bl_context = "objectmode"
    


    @classmethod
    def poll(cls, context):
        if context.object != None:
            return (context.mode in {'OBJECT', 'POSE'}) and (context.object.type == "ARMATURE")
        else:
            return False

    def draw(self, context):
        layout = self.layout

        obj1 = context.object
        scene = context.scene
        
        # row = layout.row()
        layout.label(text="Animation Ranges")
        # row = layout.row()
        layout.prop(scene.FSimMainProps, "fsim_start_frame")
        # row = layout.row()
        layout.prop(scene.FSimMainProps, "fsim_end_frame")
        row = layout.row()
        layout.operator("armature.fsim_add")
        row = layout.row()
        layout.operator("armature.fsimulate")
        row = layout.row()
        # box = layout.box()
        # box.label(text="Multi Sim Options")
        layout.operator("armature.fsim_run")
        layout.prop(scene.FSimMainProps, "fsim_copyrigs")
        layout.prop(scene.FSimMainProps, "fsim_copymesh")
        layout.prop(scene.FSimMainProps, "fsim_maxnum")
        layout.prop(scene.FSimMainProps, "fsim_startangle")

class ARMATURE_PT_FSimPropPanel(bpy.types.Panel):
    """Creates a Panel in the Tool Panel"""
    bl_label = "Main Simulation Properties"
    bl_idname = "armature.fsimproppanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FishSim"
    bl_options = {'DEFAULT_CLOSED'}
    #bl_context = "objectmode"
    
    @classmethod
    def poll(cls, context):
        if context.object != None:
            return (context.mode in {'OBJECT', 'POSE'}) and (context.object.type == "ARMATURE")
        else:
            return False

    def draw(self, context):
        #Make sure the presets directory exists
        add_preset_files()
        
        layout = self.layout

        scene = context.scene
        # row = layout.row()
        row = layout.row()
        row.menu("AMATURE_MT_fsim_presets", text=bpy.types.AMATURE_MT_fsim_presets.bl_label)
        row.operator(AddPresetFSim.bl_idname, text="", icon='TRIA_UP')
        row.operator(AddPresetFSim.bl_idname, text="", icon='TRIA_UP').remove_active = True        
        
        pFS = context.scene.FSimProps
        # row = layout.row()
        layout.label(text="Main Parameters")
        layout.prop(pFS, "pMass")
        layout.prop(pFS, "pDrag")
        layout.prop(pFS, "pPower")
        layout.prop(pFS, "pMaxFreq")
        layout.prop(pFS, "pMaxTailAngle")
        # row = layout.row()
        layout.label(text="Turning Parameters")
        layout.prop(pFS, "pAngularDrag")
        layout.prop(pFS, "pMaxSteeringAngle")
        layout.prop(pFS, "pTurnAssist")
        layout.prop(pFS, "pLeanIntoTurn")
        # row = layout.row()
        layout.label(text="Target Tracking")
        layout.prop(pFS, "pEffortGain")
        layout.prop(pFS, "pEffortIntegral")
        layout.prop(pFS, "pEffortRamp")
        # row = layout.row()
        layout.label(text="Fine Tuning")
        layout.prop(pFS, "pMaxTailFinAngle")
        layout.prop(pFS, "pTailFinPhase")
        layout.prop(pFS, "pTailFinStiffness")
        layout.prop(pFS, "pTailFinStubRatio")
        layout.prop(pFS, "pMaxSideFinAngle")
        layout.prop(pFS, "pSideFinPhase")
        layout.prop(pFS, "pChestRatio")
        layout.prop(pFS, "pChestRaise")
        layout.prop(pFS, "pMaxVerticalAngle")
        layout.prop(pFS, "pRandom")

class ARMATURE_PT_FSimPecPanel(bpy.types.Panel):
    """Creates a Panel in the Tool Panel"""
    bl_label = "Pectoral Fin Properties"
    bl_idname = "armature.fsimpecpanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FishSim"
    bl_options = {'DEFAULT_CLOSED'}
    #bl_context = "objectmode"
    
    @classmethod
    def poll(cls, context):
        if context.object != None:
            if (context.mode in {'OBJECT', 'POSE'}) and (context.object.type == "ARMATURE"):
                PecFinTopL = context.object.pose.bones.get("t_master.L")
                if PecFinTopL != None:
                    return True
        return False

    def draw(self, context):
        #Make sure the presets directory exists
        # add_preset_files()
        
        layout = self.layout

        scene = context.scene
        # row = layout.row()
        # row.menu("AMATURE_MT_fsim_presets", text=bpy.types.AMATURE_MT_fsim_presets.bl_label)
        # row.operator(AddPresetFSim.bl_idname, text="", icon='ZOOMIN')
        # row.operator(AddPresetFSim.bl_idname, text="", icon='ZOOMOUT').remove_active = True        
        
        pFS = context.scene.FSimProps
        layout.label(text="Main Pec Parameters")
        layout.prop(pFS, "pPecEffortGain")
        layout.prop(pFS, "pPecTurnAssist")
        layout.prop(pFS, "pMaxPecFreq")
        layout.prop(pFS, "pMaxPecAngle")
        layout.label(text="Pec Fin Tuning")
        layout.prop(pFS, "pPecPhase")
        layout.prop(pFS, "pPecStubRatio")
        layout.prop(pFS, "pPecStiffness")
        layout.prop(pFS, "pPecOffset")
        layout.prop(pFS, "pPecTransition")
        layout.label(text="Hover Mode Params")
        layout.prop(pFS, "pHoverDist")
        layout.prop(pFS, "pHTransTime")
        layout.prop(pFS, "pSTransTime")
        layout.prop(pFS, "pHoverTailFrc")
        layout.prop(pFS, "pHoverMaxForce")
        layout.prop(pFS, "pHoverDerate")
        layout.prop(pFS, "pHoverTilt")
        layout.label(text="Variation Tuning")
        layout.prop(pFS, "pPecDuration")
        layout.prop(pFS, "pPecDuty")
        layout.prop(pFS, "pHoverTwitch")
        layout.prop(pFS, "pHoverTwitchTime")
        layout.prop(pFS, "pPecSynch")

#Register
        
classes = (
    FSimMainProps,
    ARMATURE_OT_FSim_Add,
    ARMATURE_PT_FSim,
    ARMATURE_PT_FSimPropPanel,
    ARMATURE_PT_FSimPecPanel,
    AMATURE_MT_fsim_presets,
    AddPresetFSim,
    ARMATURE_OT_FSim_Run,
)

def register():
    from bpy.utils import register_class

    # Classes.
    for cls in classes:
        register_class(cls)

    # bpy.utils.register_class(FSimMainProps)
    bpy.types.Scene.FSimMainProps = bpy.props.PointerProperty(type=FSimMainProps)
    # bpy.utils.register_class(ARMATURE_OT_FSim_Add)
    from . import FishSim
    FishSim.registerTypes()
    from . import metarig_menu
    metarig_menu.register()
    # bpy.utils.register_class(ARMATURE_PT_FSim)
    # bpy.utils.register_class(ARMATURE_PT_FSimPropPanel)
    # bpy.utils.register_class(ARMATURE_PT_FSimPecPanel)
    # bpy.utils.register_class(AMATURE_MT_fsim_presets)
    # bpy.utils.register_class(AddPresetFSim)
    # bpy.utils.register_class(ARMATURE_OT_FSim_Run)
    


def unregister():
    from bpy.utils import unregister_class
    del bpy.types.Scene.FSimMainProps
    # bpy.utils.unregister_class(FSimMainProps)
    # bpy.utils.unregister_class(ARMATURE_OT_FSim_Add)
    from . import metarig_menu
    metarig_menu.unregister()
    from . import FishSim
    FishSim.unregisterTypes()

    # Classes.
    for cls in classes:
        unregister_class(cls)
    
    # bpy.utils.unregister_class(ARMATURE_PT_FSim)
    # bpy.utils.unregister_class(ARMATURE_PT_FSimPropPanel)
    # bpy.utils.unregister_class(ARMATURE_PT_FSimPecPanel)
    # bpy.utils.unregister_class(AMATURE_MT_fsim_presets)
    # bpy.utils.unregister_class(AddPresetFSim)
    # bpy.utils.unregister_class(ARMATURE_OT_FSim_Run)


if __name__ == "__main__":
    register()

