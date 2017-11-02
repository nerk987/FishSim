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

# version comment: V0.1.1 develop branch - metarig add

bl_info = {
    "name": "FishSim",
    "author": "Ian Huish (nerk)",
    "version": (0, 1, 0),
    "blender": (2, 78, 0),
    "location": "Toolshelf>FishSim",
    "description": "Apply fish swimming action to a Rigify Shark armature",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
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
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, StringProperty
from random import random
from bpy.types import Operator, Panel, Menu
from bl_operators.presets import AddPresetBase
# import shutil

# print(sys.modules[bpy.types.DATA_PT_rigify_buttons.__module__].__file__)    

def add_preset_files():
    presets   = bpy.utils.user_resource('SCRIPTS', "presets")
    mypresets = os.path.join(presets, "operator\\fishsim")
    if not os.path.exists(mypresets):
        os.makedirs(mypresets)    
        # print("Presets dir added:", mypresets)
    # mypath = os.path.join(mypresets, "myfile.xxx")


class FSimMainProps(bpy.types.PropertyGroup):
    fsim_targetrig = StringProperty(name="Name of the target rig", default="")  
    fsim_start_frame = IntProperty(name="Simulation Start Frame", default=1)  
    fsim_end_frame = IntProperty(name="Simulation End Frame", default=250)  
    fsim_maxnum = IntProperty(name="Maximum number of copies", default=250)  
    fsim_copyrigs = BoolProperty(name="Distribute multiple copies of the rig", default=False)  
    fsim_copymesh = BoolProperty(name="Distribute multiple copies of meshes", default=False)  
    fsim_multisim = BoolProperty(name="Simulate the multiple rigs", default=False)  
    fsim_startangle = FloatProperty(name="Angle to Target", default=0.0)
    



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
        TargetRig = context.object
        
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
        bound_box.draw_type = 'WIRE'
        bound_box.hide_render = True
        bound_box.cycles_visibility.camera = False
        bound_box.cycles_visibility.diffuse = False
        bound_box.cycles_visibility.shadow = False
        bound_box["FSim"] = "FSim_"+TargetRig.name[:3]
        # if "FSim" in bound_box:
            # print("FSim Found")
        bound_box.select = False
        #context.active_pose_bone = TargetRoot
        
        return {'FINISHED'}



#UI Panels
class AMATURE_MT_fsim_presets(Menu):
    bl_label = "FishSim Presets"
    preset_subdir = "../addons/fishsim/presets"
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
        "pFS.pTailFinGain",
        "pFS.pTailFinStiffness",
        "pFS.pTailFinStubRatio",
        "pFS.pMaxSideFinAngle",
        "pFS.pSideFinGain",
        "pFS.pSideFinStiffness",
        "pFS.pChestRatio",
        "pFS.pChestRaise",
        "pFS.pMaxVerticalAngle",
        "pFS.pRandom",
        ]

    # where to store the preset
    preset_subdir = "../addons/fishsim/presets"

class ARMATURE_PT_FSim(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "FishSim"
    bl_idname = "armature.fsim"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
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
        
        row = layout.row()
        row.label("Animation Ranges")
        row = layout.row()
        row.prop(scene.FSimMainProps, "fsim_start_frame")
        row = layout.row()
        row.prop(scene.FSimMainProps, "fsim_end_frame")
        row = layout.row()
        row.operator("armature.fsim_add")
        row = layout.row()
        row.operator("armature.fsimulate")
        row = layout.row()
        box = layout.box()
        # box.label("Multi Sim Options")
        box.operator("armature.fsim_run")
        box.prop(scene.FSimMainProps, "fsim_copyrigs")
        box.prop(scene.FSimMainProps, "fsim_copymesh")
        box.prop(scene.FSimMainProps, "fsim_maxnum")
        box.prop(scene.FSimMainProps, "fsim_startangle")

class ARMATURE_PT_FSimPropPanel(bpy.types.Panel):
    """Creates a Panel in the Tool Panel"""
    bl_label = "Simulation Properties"
    bl_idname = "armature.fsimproppanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "FishSim"
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
        row = layout.row()
        row.menu("AMATURE_MT_fsim_presets", text=bpy.types.AMATURE_MT_fsim_presets.bl_label)
        row.operator(AddPresetFSim.bl_idname, text="", icon='ZOOMIN')
        row.operator(AddPresetFSim.bl_idname, text="", icon='ZOOMOUT').remove_active = True        
        
        pFS = context.scene.FSimProps
        box = layout.box()
        box.label("Main Parameters")
        box.prop(pFS, "pMass")
        box.prop(pFS, "pDrag")
        box.prop(pFS, "pPower")
        box.prop(pFS, "pMaxFreq")
        box.prop(pFS, "pMaxTailAngle")
        box = layout.box()
        box.label("Turning Parameters")
        box.prop(pFS, "pAngularDrag")
        box.prop(pFS, "pMaxSteeringAngle")
        box.prop(pFS, "pTurnAssist")
        box.prop(pFS, "pLeanIntoTurn")
        box = layout.box()
        box.label("Target Tracking")
        box.prop(pFS, "pEffortGain")
        box.prop(pFS, "pEffortIntegral")
        box.prop(pFS, "pEffortRamp")
        box = layout.box()
        box.label("Fine Tuning")
        box.prop(pFS, "pMaxTailFinAngle")
        box.prop(pFS, "pTailFinGain")
        box.prop(pFS, "pTailFinStiffness")
        box.prop(pFS, "pTailFinStubRatio")
        box.prop(pFS, "pMaxSideFinAngle")
        box.prop(pFS, "pSideFinGain")
        box.prop(pFS, "pSideFinStiffness")
        box.prop(pFS, "pChestRatio")
        box.prop(pFS, "pChestRaise")
        box.prop(pFS, "pMaxVerticalAngle")
        box.prop(pFS, "pRandom")


def register():
    bpy.utils.register_class(FSimMainProps)
    bpy.types.Scene.FSimMainProps = bpy.props.PointerProperty(type=FSimMainProps)
    bpy.utils.register_class(ARMATURE_OT_FSim_Add)
    from . import FishSim
    FishSim.registerTypes()
    from . import metarig_menu
    metarig_menu.register()
    bpy.utils.register_class(ARMATURE_PT_FSim)
    bpy.utils.register_class(ARMATURE_PT_FSimPropPanel)
    bpy.utils.register_class(AMATURE_MT_fsim_presets)
    bpy.utils.register_class(AddPresetFSim)
    # shutil.copytree("")
    


def unregister():
    del bpy.types.Scene.FSimMainProps
    bpy.utils.unregister_class(FSimMainProps)
    bpy.utils.unregister_class(ARMATURE_OT_FSim_Add)
    from . import FishSim
    FishSim.unregisterTypes()
    from . import metarig_menu
    metarig_menu.unregister()
    bpy.utils.unregister_class(ARMATURE_PT_FSim)
    bpy.utils.unregister_class(ARMATURE_PT_FSimPropPanel)
    bpy.utils.unregister_class(AMATURE_MT_fsim_presets)
    bpy.utils.unregister_class(AddPresetFSim)


if __name__ == "__main__":
    register()

