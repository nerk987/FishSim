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
# version comment: reorganise branch - first split
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

import bpy
import mathutils,  math, os
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, StringProperty
from random import random

class FSimMainProps(bpy.types.PropertyGroup):
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
        if "FSim" in bound_box:
            print("FSim Found")
        bound_box.select = False
        #context.active_pose_bone = TargetRoot
        
        return {'FINISHED'}



#UI Panels

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
        # row = layout.row()
        # row.label(text="Active object is: " + obj1.name)
        #row = layout.row()
        #row.prop(obj1, "name")
        row = layout.row()
        row.label("Animation Range")
        row = layout.row()
        row.prop(scene.FSimMainProps, "fsim_start_frame")
        row = layout.row()
        row.prop(scene.FSimMainProps, "fsim_end_frame")
        row = layout.row()
        row.operator("armature.fsim_add")
        row = layout.row()
        row.operator("armature.fsim_run")
        #row = layout.row()
        #row.operator("armature.fsim_populate")
        box = layout.box()
        box.label("Multi Sim Options")
        box.prop(scene.FSimMainProps, "fsim_copyrigs")
        box.prop(scene.FSimMainProps, "fsim_copymesh")
        box.prop(scene.FSimMainProps, "fsim_multisim")
        box.prop(scene.FSimMainProps, "fsim_maxnum")
        box.prop(scene.FSimMainProps, "fsim_startangle")

        


def register():
    bpy.utils.register_class(FSimMainProps)
    bpy.types.Scene.FSimMainProps = bpy.props.PointerProperty(type=FSimMainProps)
    bpy.utils.register_class(ARMATURE_OT_FSim_Add)
    from . import FishSim
    FishSim.registerTypes()
    bpy.utils.register_class(ARMATURE_PT_FSim)


def unregister():
    del bpy.types.Scene.FSimMainProps
    bpy.utils.unregister_class(FSimMainProps)
    bpy.utils.unregister_class(ARMATURE_OT_FSim_Add)
    from . import FishSim
    FishSim.unregisterTypes()
    bpy.utils.unregister_class(ARMATURE_PT_FSim)


if __name__ == "__main__":
    register()

