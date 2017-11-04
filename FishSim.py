# ##### BEGIN GPL LICENSE BLOCK #####
#
#  FishSim  -- a script to apply a fish swimming simulation to an armature
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

# version comment: V0.1.2 develop branch - Tail angle fix

import bpy
import mathutils,  math, os
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, StringProperty
from random import random





class FSimProps(bpy.types.PropertyGroup):
    
    #State Variables
    sVelocity = FloatProperty(name="Velocity", description="Speed", default=0.0, min=0)
    sEffort = FloatProperty(name="Effort", description="The effort going into swimming", default=1.0, min=0)
    sTurn = FloatProperty(name="Turn", description="The intent to go left of right (positive is right)", default=0.0)
    sRise = FloatProperty(name="Rise", description="The intent to go up or down (positive is up", default=0.0)
    sFreq = FloatProperty(name="Frequency", description="Current frequency of tail movement in frames per cycle", default=0.0)
    sTailAngle = FloatProperty(name="Tail Angle", description="Current max tail angle in degrees", default=0.0)
    sTailAngleOffset = FloatProperty(name="Tail Angle Offset", description="Offset angle for turning in degrees", default=0.0)

    #Property declaration
    pMass = FloatProperty(name="Mass", description="Total Mass", default=30.0, min=0, max=3000.0)
    pDrag = FloatProperty(name="Drag", description="Total Drag", default=8.0, min=0, max=3000.0)
    pPower = FloatProperty(name="Power", description="Forward force for given tail fin speed and angle", default=20.0, min=0)
    pMaxFreq = FloatProperty(name="Stroke Period", description="Maximum frequency of tail movement in frames per cycle", default=15.0)
    pEffortGain = FloatProperty(name="Effort Gain", description="The amount of effort required for a change in distance to target", default=0.5, min=0.0)
    pEffortIntegral = FloatProperty(name="Effort Integral", description="The amount of effort required for a continuing distance to target", default=0.5, min=0.0)
    pEffortRamp = FloatProperty(name="Effort Ramp", description="First Order factor for ramping up effort", default=0.2, min=0.0, max=0.6)
    pAngularDrag = FloatProperty(name="AngularDrag", description="Resistance to changing direction", default=1.0, min=0)
    pTurnAssist = FloatProperty(name="TurnAssist", description="Fake Turning effect (0 - 10)", default=3.0, min=0)
    pMaxTailAngle = FloatProperty(name="Max Tail Angle", description="Max tail angle", default=15.0, min=0, max=30.0)
    pMaxSteeringAngle = FloatProperty(name="Max Steering Angle", description="Max steering tail angle", default=15.0, min=0, max=40.0)
    pMaxVerticalAngle = FloatProperty(name="Max Vertical Angle", description="Max steering angle for vertical", default=0.1, min=0, max=40.0)
    pMaxTailFinAngle = FloatProperty(name="Max Tail Fin Angle", description="Max tail fin angle", default=15.0, min=0, max=30.0)
    pTailFinGain = FloatProperty(name="Tail Fin Gain", description="Tail Fin speed of response to movement", default=5.0, min=0, max=25.0)
    pTailFinStiffness = FloatProperty(name="Tail Fin Stiffness", description="Tail Fin Stiffness", default=0.2, min=0, max=1.0)
    pTailFinStubRatio = FloatProperty(name="Tail Fin Stub Ratio", description="Ratio for the bottom part of the tail", default=0.3, min=0, max=3.0)
    pMaxSideFinAngle = FloatProperty(name="Max Side Fin Angle", description="Max side fin angle", default=15.0, min=0, max=60.0)
    pSideFinGain = FloatProperty(name="Side Fin Gain", description="Side Fin speed of response to movement", default=2.0, min=0, max=100.0)
    pSideFinStiffness = FloatProperty(name="Side Fin Stiffness", description="Side Fin Stiffness", default=0.2, min=0, max=10.0)
    pChestRatio = FloatProperty(name="Chest Ratio", description="Ratio of the front of the fish to the rear", default=0.5, min=0, max=2.0)
    pChestRaise = FloatProperty(name="Chest Raise Factor", description="Chest raises during turning", default=1.0, min=0, max=20.0)
    pLeanIntoTurn = FloatProperty(name="LeanIntoTurn", description="Amount it leans into the turns", default=1.0, min=0, max=20.0)
    pRandom = FloatProperty(name="Random", description="Random amount", default=0.25, min=0, max=1.0)

    
    
    
class ARMATURE_OT_FSimulate(bpy.types.Operator):
    """Simulate all armatures with a similar name to selected"""
    bl_idname = "armature.fsimulate"
    bl_label = "Simulate"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    
    _timer = None
    sRoot = None
    sTorso = None
    sSpine_master = None
    sBack_fin1 = None
    sBack_fin2 = None
    sBack_fin_middle = None
    sChest = None
    sSideFinL = None
    sSideFinR = None
    sState = 0.0
    sAngularForceV = 0.0
    sTargetProxy = None
    rMaxTailAngle = 0.0
    rMaxFreq = 0.0
    sTargetRig = None
    sOldRqdEffort = 0.0
    sOld_back_fin = None
    sArmatures = []
    nArmature = 0
    
    def armature_list(self, scene, sFPM):
        self.sArmatures = []
        for obj in scene.objects:
            if obj.type == "ARMATURE" and obj.name[:3] == self.sTargetRig.name[:3]:
                root = obj.pose.bones.get("root")
                if root != None:
                    if 'TargetProxy' in root:
                        self.sArmatures.append(obj.name)
        self.nArmature = len(self.sArmatures) - 1
        # print("List: ", self.sArmatures)

    
    def RemoveKeyframes(self, armature, bones):
        dispose_paths = []
        #dispose_paths.append('pose.bones["{}"].rotation_quaternion'.format(bone.name))
        for fcurve in armature.animation_data.action.fcurves:
            if (fcurve.data_path == "location" or fcurve.data_path == "rotation_euler"):
                armature.animation_data.action.fcurves.remove(fcurve)
        for bone in bones:
            #bone.rotation_mode='XYZ'
            #dispose_paths.append('pose.bones["{}"].rotation_euler'.format(bone.name))
            dispose_paths.append('pose.bones["{}"].rotation_quaternion'.format(bone.name))
            dispose_paths.append('pose.bones["{}"].scale'.format(bone.name))
        dispose_curves = [fcurve for fcurve in armature.animation_data.action.fcurves if fcurve.data_path in dispose_paths]
        for fcurve in dispose_curves:
            armature.animation_data.action.fcurves.remove(fcurve)

    #Set Effort and Direction properties to try and reach the target.
    def Target(self, TargetRig, TargetProxy):
        RigDirn = mathutils.Vector((0,-1,0)) * TargetRig.matrix_world.inverted()
        #print("RigDirn: ", RigDirn)
        
        #distance to target
        if TargetProxy != None:
            TargetDirn = (TargetProxy.matrix_world.to_translation() - TargetRig.location)
        else:
            TargetDirn = mathutils.Vector((0,-10,0))
        DifDot = TargetDirn.dot(RigDirn)
        
        #horizontal angle to target - limit max turning effort at 90 deg
        RigDirn2D = mathutils.Vector((RigDirn.x, RigDirn.y))
        TargetDirn2D = mathutils.Vector((TargetDirn.x, TargetDirn.y))
        AngleToTarget = math.degrees(RigDirn2D.angle_signed(TargetDirn2D, math.radians(180)))
        DirectionEffort = AngleToTarget/90.0
        DirectionEffort = min(1.0,DirectionEffort)
        DirectionEffort = max(-1.0,DirectionEffort)
        
        #vertical angle to target - limit max turning effort at 20 deg
        RigDirn2DV = mathutils.Vector(((RigDirn.y**2 + RigDirn.x**2)**0.5, RigDirn.z))
        TargetDirn2DV = mathutils.Vector(((TargetDirn.y**2 + TargetDirn.x**2)**0.5, TargetDirn.z))
        AngleToTargetV = math.degrees(RigDirn2DV.angle_signed(TargetDirn2DV, math.radians(180)))
        DirectionEffortV = AngleToTargetV/20.0
        DirectionEffortV = min(1.0,DirectionEffortV)
        DirectionEffortV = max(-1.0,DirectionEffortV)
        
        #Return normalised required effort, turning factor, and ascending factor
        return DifDot,DirectionEffort,DirectionEffortV
        
    #Handle the object movement
    def ObjectMovment(self, TargetRig, ForwardForce, AngularForce, AngularForceV, nFrame, TargetProxy, pFS):
        RigDirn = mathutils.Vector((0,-1,0)) * TargetRig.matrix_world.inverted()
        #Total force is tail force - drag
        DragForce = pFS.pDrag * pFS.sVelocity ** 2.0
        pFS.sVelocity += (ForwardForce - DragForce) / pFS.pMass
        #print("Fwd, Drag: ", ForwardForce, DragForce)
        TargetRig.location += pFS.sVelocity * RigDirn
        TargetRig.keyframe_insert(data_path='location',  frame=(nFrame))
        
        #Let's be simplistic - just rotate object based on angluar force
        TargetRig.rotation_euler.z += math.radians(AngularForce)
        TargetRig.rotation_euler.x += math.radians(AngularForceV)
        TargetRig.keyframe_insert(data_path='rotation_euler',  frame=(nFrame))
        
    #Handle the movement of the bones within the armature        
    def BoneMovement(self, context):
    
        
        scene = context.scene
        pFS = scene.FSimProps
        pFSM = scene.FSimMainProps
        startFrame = pFSM.fsim_start_frame
        endFrame = pFSM.fsim_end_frame
        
        #Get the current Target Rig
        TargetRig = scene.objects.get(self.sArmatures[self.nArmature])
        self.sTargetRig = TargetRig
    
        #Check the required Rigify bones are present
        self.sRoot = TargetRig.pose.bones.get("root")
        self.sTorso = TargetRig.pose.bones.get("torso")
        self.sSpine_master = TargetRig.pose.bones.get("spine_master")
        self.sBack_fin1 = TargetRig.pose.bones.get("back_fin_masterBk.001")
        self.sBack_fin2 = TargetRig.pose.bones.get("back_fin_masterBk")
        self.sBack_fin_middle = TargetRig.pose.bones.get("DEF-back_fin.T.001.Bk")
        self.sChest = TargetRig.pose.bones.get("chest")
        self.sSideFinL = TargetRig.pose.bones.get("side_fin.L")
        self.sSideFinR = TargetRig.pose.bones.get("side_fin.R")
        if (self.sSpine_master is None) or (self.sTorso is None) or (self.sChest is None) or (self.sBack_fin1 is None) or (self.sBack_fin2 is None) or (self.sBack_fin_middle is None) or (self.sSideFinL is None) or (self.sSideFinR is None):
            self.report({'ERROR'}, "Sorry, this addon needs a Rigify rig generated from a Shark Metarig")
            print("Not an Suitable Rigify Armature")
            return 0,0
            
        #initialise state variabiles
        self.sState = 0.0
        self.AngularForceV = 0.0
            
        #Get TargetProxy object details
        try:
            TargetProxyName = self.sRoot["TargetProxy"]
            self.sTargetProxy = bpy.data.objects[TargetProxyName]
        except:
            self.sTargetProxy = None

        #Go back to the start before removing keyframes to remember starting point
        context.scene.frame_set(startFrame)
       
        #Delete existing keyframes
        try:
            self.RemoveKeyframes(TargetRig, [self.sSpine_master, self.sBack_fin1, self.sBack_fin2, self.sChest, self.sSideFinL, self.sSideFinR])
        except:
            pass
            # print("info: no keyframes")
        
        #record to previous tail position
        context.scene.frame_set(startFrame)
        context.scene.update()
        
        #randomise parameters
        rFact = pFS.pRandom
        self.rMaxTailAngle = pFS.pMaxTailAngle * (1 + (random() * 2.0 - 1.0) * rFact)
        self.rMaxFreq = pFS.pMaxFreq * (1 + (random() * 2.0 - 1.0) * rFact)
        
        
    def ModalMove(self, context):
        scene = context.scene
        pFS = scene.FSimProps
        pFSM = scene.FSimMainProps
        startFrame = pFSM.fsim_start_frame
        endFrame = pFSM.fsim_end_frame
        
        nFrame = scene.frame_current
        
        # print("Target Rig and Proxy: ", self.sTargetRig.name, self.sTargetProxy.name)
        
        
        #Get the effort and direction change to head toward the target
        RqdEffort, RqdDirection, RqdDirectionV = self.Target(self.sTargetRig, self.sTargetProxy)
        if nFrame == startFrame:
            self.sOldRqdEffort = RqdEffort
        TargetEffort = pFS.pEffortGain * (pFS.pEffortIntegral * RqdEffort + (RqdEffort - self.sOldRqdEffort))
        self.sOldRqdEffort = RqdEffort
        pFS.sEffort = pFS.pEffortGain * RqdEffort * pFS.pEffortRamp + pFS.sEffort * (1.0-pFS.pEffortRamp)
        pFS.sEffort = min(pFS.sEffort, 1.0)
        #print("Required, Effort:", RqdEffort, pFS.sEffort)
        
        #Convert effort into tail frequency and amplitude
        pFS.pFreq = self.rMaxFreq * (1.0/(pFS.sEffort+ 0.01))
        pFS.pTailAngle = self.rMaxTailAngle * pFS.sEffort
        
        #Convert direction into Tail angle
        pFS.sTailAngleOffset = pFS.sTailAngleOffset * (1 - pFS.pEffortRamp) + RqdDirection * pFS.pMaxSteeringAngle * pFS.pEffortRamp
        #print("TailOffset: ", pFS.sTailAngleOffset)
        
        
        #Spine Movement
        self.sState = self.sState + 360.0 / pFS.pFreq
        xTailAngle = math.sin(math.radians(self.sState))*math.radians(pFS.pTailAngle) + math.radians(pFS.sTailAngleOffset)
        #print("TailAngle", xTailAngle)
        self.sSpine_master.rotation_quaternion = mathutils.Quaternion((0.0, 0.0, 1.0), xTailAngle)
        self.sSpine_master.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        ChestRot = mathutils.Quaternion((0.0, 0.0, 1.0), -xTailAngle * pFS.pChestRatio - math.radians(pFS.sTailAngleOffset))
        self.sChest.rotation_quaternion = ChestRot * mathutils.Quaternion((1.0, 0.0, 0.0), -math.fabs(math.radians(pFS.sTailAngleOffset))*pFS.pChestRaise)
        #print("Torso:", pFS.sTailAngleOffset)
        self.sTorso.rotation_quaternion = mathutils.Quaternion((0.0, 1.0, 0.0), -math.radians(pFS.sTailAngleOffset)*pFS.pLeanIntoTurn)
        self.sChest.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        self.sTorso.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        #context.scene.update()

        #Tail Movment
        if (nFrame == startFrame):
            back_fin_dif = 0
        else:
            back_fin_dif = (self.sBack_fin_middle.matrix.decompose()[0].x - self.sOld_back_fin.x)
        self.sOld_back_fin = self.sBack_fin_middle.matrix.decompose()[0]
    
        #Tail Fin angle based on Tail movement
        pMaxTailScale = pFS.pMaxTailFinAngle * 0.4 / 30.0
        currentTailScale = self.sBack_fin1.scale[1]
        if (back_fin_dif < 0) :
            TailScaleIncr = (1 + pMaxTailScale - currentTailScale) * pFS.pTailFinGain * math.fabs(back_fin_dif)
            #print("Positive scale: ", TailScaleIncr)
        else:
            TailScaleIncr = (1 - pMaxTailScale - currentTailScale) * pFS.pTailFinGain * math.fabs(back_fin_dif)
            #print("Negative scale: ", TailScaleIncr)
        
        #Tail Fin stiffness factor
        TailFinStiffnessIncr = (1 - currentTailScale) * pFS.pTailFinStiffness
        
        if (nFrame == startFrame):
            self.sBack_fin1_scale = 1.0
        else:
            self.sBack_fin1_scale = self.sBack_fin1.scale[1] + TailScaleIncr + TailFinStiffnessIncr
            
        #Limit Tail Fin maximum deflection    
        if (self.sBack_fin1_scale > (pMaxTailScale + 1)):
            self.sBack_fin1_scale = pMaxTailScale + 1
        if (self.sBack_fin1_scale < (-pMaxTailScale + 1)):
            self.sBack_fin1_scale = -pMaxTailScale + 1
        self.sBack_fin1.scale[1] = self.sBack_fin1_scale
        self.sBack_fin2.scale[1] = 1 - (1 - self.sBack_fin1_scale) * pFS.pTailFinStubRatio
        #scene.update()
        #print("New Scale:", self.sBack_fin1.scale[1])
        self.sBack_fin1.keyframe_insert(data_path='scale',  frame=(nFrame))
        self.sBack_fin2.keyframe_insert(data_path='scale',  frame=(nFrame))
        
        #Side Fin angle based on Tail movement
        pMaxSideFinAngle = pFS.pMaxSideFinAngle
        currentSideFinRot = math.degrees(self.sSideFinL.rotation_quaternion.to_euler().x)
        if (back_fin_dif < 0) :
            SideIncr = (pMaxSideFinAngle - currentSideFinRot) * pFS.pSideFinGain * math.fabs(back_fin_dif)
            #print("Side Positive scale: ", SideIncr)
        else:
            SideIncr = (-pMaxSideFinAngle - currentSideFinRot) * pFS.pSideFinGain * math.fabs(back_fin_dif)
            #print("Side Negative scale: ", SideIncr)
        
        #Side Fin stiffness factor
        SideFinStiffnessIncr = -currentSideFinRot * pFS.pSideFinStiffness
        
        if (nFrame == startFrame):
            SideFinRot = 0.0
        else:
            SideFinRot = currentSideFinRot + SideIncr + SideFinStiffnessIncr
            #print("Current, incr, stiff: ", currentSideFinRot, SideIncr, SideFinStiffnessIncr)

        #Limit Side Fin maximum deflection    
        if (SideFinRot > pMaxSideFinAngle):
            SideFinRot = pMaxSideFinAngle
        if (SideFinRot < -pMaxSideFinAngle):
            SideFinRot = -pMaxSideFinAngle
        self.sSideFinL.rotation_quaternion = mathutils.Quaternion((1,0,0), math.radians(-SideFinRot))
        self.sSideFinR.rotation_quaternion = mathutils.Quaternion((1,0,0), math.radians(SideFinRot))
        #scene.update()
        self.sSideFinL.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        self.sSideFinR.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        
        #Do Object movment with Forward force and Angular force
        TailFinAngle = (self.sBack_fin1_scale - 1.0) * 30.0 / 0.4
        TailFinAngleForce = math.sin(math.radians(TailFinAngle))
        ForwardForce = -back_fin_dif * TailFinAngleForce * pFS.pPower
        
        #Angular force due to 'swish'
        AngularForce = back_fin_dif  / pFS.pAngularDrag
        
        #Angular force due to rudder effect
        AngularForce += -xTailAngle * pFS.sVelocity / pFS.pAngularDrag
        
        #Fake Angular force to make turning more effective
        AngularForce += -(pFS.sTailAngleOffset/pFS.pMaxSteeringAngle) * pFS.pTurnAssist
        
        #Angular force for vertical movement
        self.sAngularForceV = self.sAngularForceV * (1 - pFS.pEffortRamp) + RqdDirectionV * pFS.pMaxVerticalAngle
        
        
        #print("TailFinAngle, AngularForce", xTailAngle, AngularForce)
        self.ObjectMovment(self.sTargetRig, ForwardForce, AngularForce, self.sAngularForceV, nFrame, self.sTargetProxy, pFS)
        
        #Go to next frame, or finish
        wm = context.window_manager
        # print("Frame: ", nFrame)
        if nFrame == endFrame:
            return 0
        else:
            wm.progress_update((len(self.sArmatures) - self.nArmature)*99.0/len(self.sArmatures))
            context.scene.frame_set(nFrame + 1)
            return 1
        

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            modal_rtn = self.ModalMove(context)
            if modal_rtn == 0:
                print("nArmature:", self.nArmature)
                #Go to the next rig if applicable
                context.scene.frame_set(context.scene.FSimMainProps.fsim_start_frame)
                if self.nArmature > 0:
                    self.nArmature -= 1
                    self.BoneMovement(context) 

                else:
                    wm = context.window_manager
                    wm.progress_end()
                    return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        sFPM = context.scene.FSimMainProps
        # try:
            # self.sTargetRig = scene.objects.get(sFPM.fsim_targetrig)
        # except:
        self.sTargetRig = context.object
        scene = context.scene
        
        #Load a list of the relevant armatures
        self.armature_list(scene, sFPM)
        
        #Progress bar
        wm = context.window_manager
        wm.progress_begin(0.0,100.0)

        scene.frame_set(sFPM.fsim_start_frame)
        self.BoneMovement(context) 
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.001, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def draw(self, context):
        pFS = context.scene.FSimProps
        layout = self.layout
        layout.operator('screen.repeat_last', text="Repeat", icon='FILE_REFRESH' )
        
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


class ARMATURE_OT_FSim_Run(bpy.types.Operator):
    """Simulate and add keyframes for the armature to make it swim towards the target"""
    bl_label = "Copy Models"
    bl_idname = "armature.fsim_run"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    
    # add_preset_files()
    
    root = None

    

    def CopyChildren(self, scene, src_obj, new_obj):
        for childObj in src_obj.children:
            # print("Copying child: ", childObj.name)
            new_child = childObj.copy()
            new_child.data = childObj.data.copy()
            new_child.animation_data_clear()
            new_child.location = childObj.location - src_obj.location
            new_child.parent = new_obj
            scene.objects.link(new_child)
            new_child.select = True
            for mod in new_child.modifiers:
                if mod.type == "ARMATURE":
                    mod.object = new_obj

    
    def CopyRigs(self, context):
        # print("Populate")
        
        scene = context.scene
        src_obj = context.object
        if src_obj.type != 'ARMATURE':
            return {'CANCELLED'}
        src_obj.select = False
        
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
                scene.update()
                
                #if a rig hasn't already been paired with this target, and it's the right target type for this rig, then add a duplicated rig at this location if 'CopyRigs' is selected
                if (obj.name not in armatures) and (obj["FSim"][-3:] == src_obj.name[:3]):
                    # print("time to duplicate")

                    if scene.FSimMainProps.fsim_copyrigs:
                        #If there is not already a matching armature, duplicate the template and update the link field
                        new_obj = src_obj.copy()
                        new_obj.data = src_obj.data.copy()
                        new_obj.animation_data_clear()
                        scene.objects.link(new_obj)
                        new_obj.location = obj.matrix_world.to_translation()
                        new_obj.rotation_euler = obj.rotation_euler
                        new_obj.rotation_euler.z += math.radians(scene.FSimMainProps.fsim_startangle)
                        new_root = new_obj.pose.bones.get('root')
                        new_root['TargetProxy'] = obj.name
                        new_root.scale = (new_root.scale.x * obj.scale.x, new_root.scale.y * obj.scale.y, new_root.scale.z * obj.scale.z)
                        scene.objects.active = new_obj
                        new_obj.select = True
                        src_obj.select = False
                        # if scene.FSimMainProps.fsim_multisim and new_obj.name != src_obj.name:
                            # # self.BoneMovement(new_obj, scene.FSimMainProps.fsim_start_frame, scene.FSimMainProps.fsim_end_frame, context)
                            # bpy.ops.armature.fsimulate()
                        
                        #if 'CopyMesh' is selected duplicate the dependents and re-link
                        if scene.FSimMainProps.fsim_copymesh:
                            self.CopyChildren(scene, src_obj, new_obj)

                #If there's already a matching rig, then just update it
                elif obj["FSim"][-3:] == src_obj.name[:3]:
                    # print("matching armature", armatures[obj.name])
                    TargRig = scene.objects.get(armatures[obj.name])
                    if TargRig is not None:
                        #reposition if required
                        if scene.FSimMainProps.fsim_copyrigs:
                            TargRig.animation_data_clear()
                            TargRig.location = obj.matrix_world.to_translation()
                            TargRig.rotation_euler = obj.rotation_euler
                            TargRig.rotation_euler.z += math.radians(scene.FSimMainProps.fsim_startangle)
                        
                        #if no children, and the 'copymesh' flag set, then copy the associated meshes
                        if scene.FSimMainProps.fsim_copymesh and len(TargRig.children) < 1:
                            self.CopyChildren(scene, src_obj, TargRig)
                        
                        #Leave the just generated objects selected
                        scene.objects.active = TargRig
                        TargRig.select = True
                        src_obj.select = False
                        for childObj in TargRig.children:
                            childObj.select = True
                        for childObj in src_obj.children:
                            childObj.select = False

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

        


def registerTypes():
    bpy.utils.register_class(FSimProps)
    bpy.types.Scene.FSimProps = bpy.props.PointerProperty(type=FSimProps)
    bpy.utils.register_class(ARMATURE_OT_FSim_Run)
    bpy.utils.register_class(ARMATURE_OT_FSimulate)

def unregisterTypes():
    del bpy.types.Scene.FSimProps
    bpy.utils.unregister_class(FSimProps)
    bpy.utils.unregister_class(ARMATURE_OT_FSim_Run)
    bpy.utils.unregister_class(ARMATURE_OT_FSimulate)


if __name__ == "__main__":
    register()

