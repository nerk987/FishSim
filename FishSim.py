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

# version comment: V4.00.0 - Goldfish Version - Blender 4.00

import bpy
import mathutils,  math, os
from bpy.props import FloatProperty, FloatVectorProperty, IntProperty, BoolProperty, EnumProperty, StringProperty
from random import random





class FSimProps(bpy.types.PropertyGroup):
    
    #State Variables
    sVelocity : FloatVectorProperty(name="Velocity", description="Speed", subtype='XYZ', default=(0.0,0.0,0.0), min=-5.0, max=5.0)
    sEffort : FloatProperty(name="Effort", description="The effort going into swimming", default=1.0, min=0)
    sTurn : FloatProperty(name="Turn", description="The intent to go left of right (positive is right)", default=0.0)
    sRise : FloatProperty(name="Rise", description="The intent to go up or down (positive is up", default=0.0)
    sFreq : FloatProperty(name="Frequency", description="Current frequency of tail movement in frames per cycle", default=0.0)
    sTailAngle : FloatProperty(name="Tail Angle", description="Current max tail angle in degrees", default=0.0)
    sTailAngleOffset : FloatProperty(name="Tail Angle Offset", description="Offset angle for turning in degrees", default=0.0)

    #Property declaration
    pMass : FloatProperty(name="Mass", description="Total Mass", default=30.0, min=0, max=3000.0)
    pDrag : FloatProperty(name="Drag", description="Total Drag", default=8.0, min=0, max=3000.0)
    pPower : FloatProperty(name="Power", description="Forward force for given tail fin speed and angle", default=1.0, min=0)
    pMaxFreq : FloatProperty(name="Stroke Period", description="Maximum frequency of tail movement in frames per cycle", default=15.0)
    pEffortGain : FloatProperty(name="Effort Gain", description="The amount of effort required for a change in distance to target", default=0.5, min=0.0)
    pEffortIntegral : FloatProperty(name="Effort Integral", description="The amount of effort required for a continuing distance to target", default=0.5, min=0.0)
    pEffortRamp : FloatProperty(name="Effort Ramp", description="First Order factor for ramping up effort", default=0.2, min=0.0, max=0.6)
    pAngularDrag : FloatProperty(name="AngularDrag", description="Resistance to changing direction", default=1.0, min=0)
    pTurnAssist : FloatProperty(name="TurnAssist", description="Fake Turning effect (0 - 10)", default=3.0, min=0)
    pMaxTailAngle : FloatProperty(name="Max Tail Angle", description="Max tail angle", default=15.0, min=0, max=30.0)
    pMaxSteeringAngle : FloatProperty(name="Max Steering Angle", description="Max steering tail angle", default=15.0, min=0, max=40.0)
    pMaxVerticalAngle : FloatProperty(name="Max Vertical Angle", description="Max steering angle for vertical", default=0.1, min=0, max=40.0)
    pMaxTailFinAngle : FloatProperty(name="Max Tail Fin Angle", description="Max tail fin angle", default=15.0, min=0, max=30.0)
    pTailFinPhase : FloatProperty(name="Tail Fin Phase", description="Tail Fin phase offset from tail movement in degrees", default=90.0, min=45.0, max=135.0)
    pTailFinStiffness : FloatProperty(name="Tail Fin Stiffness", description="Tail Fin Stiffness", default=1.0, min=0, max=2.0)
    pTailFinStubRatio : FloatProperty(name="Tail Fin Stub Ratio", description="Ratio for the bottom part of the tail", default=0.3, min=0, max=3.0)
    pMaxSideFinAngle : FloatProperty(name="Max Side Fin Angle", description="Max side fin angle", default=5.0, min=0, max=60.0)
    pSideFinPhase : FloatProperty(name="Side Fin Phase", description="Side Fin phase offset from tail movement in degrees", default=90.0, min=45.0, max=135.0)
    # pSideFinStiffness : FloatProperty(name="Side Fin Stiffness", description="Side Fin Stiffness", default=0.2, min=0, max=10.0)
    pChestRatio : FloatProperty(name="Chest Ratio", description="Ratio of the front of the fish to the rear", default=0.5, min=0, max=2.0)
    pChestRaise : FloatProperty(name="Chest Raise Factor", description="Chest raises during turning", default=1.0, min=0, max=20.0)
    pLeanIntoTurn : FloatProperty(name="LeanIntoTurn", description="Amount it leans into the turns", default=1.0, min=0, max=20.0)
    pRandom : FloatProperty(name="Random", description="Random amount", default=0.25, min=0, max=1.0)

    #Pectoral Fin Properties
    pPecEffortGain : FloatProperty(name="Pectoral Effort Gain", description="Amount of effort to maintain position with 1.0 trying very hard to maintain", default=0.25, min=0, max=1.0)
    pPecTurnAssist : FloatProperty(name="Pectoral Turn Assist", description="Turning Speed while hovering 5 is fast, .2 is slow", default=1.0, min=0, max=20.0)

    pMaxPecFreq : FloatProperty(name="Pectoral Stroke Period", description="Maximum frequency of pectoral fin movement in frames per cycle", default=15.0, min=0)
    pMaxPecAngle : FloatProperty(name="Max Pec Fin Angle", description="Max Pectoral Fin Angle", default=20.0, min=0, max=80)
    pPecPhase : FloatProperty(name="Pec Fin Tip Phase", description="How far the fin tip lags behind the main movement in degrees", default=90.0, min=0, max=180)
    pPecStubRatio : FloatProperty(name="Pectoral Stub Ratio", description="Ratio for the bottom part of the pectoral fin", default=0.7, min=0, max=2)
    pPecStiffness : FloatProperty(name="Pec Fin Stiffness", description="Pectoral fin stiffness, with 1.0 being very stiff", default=0.7, min=0, max=2)
    pHTransTime : FloatProperty(name="Hover Transition Time", description="Speed of transition between swim and hover in seconds", default=0.5, min=0, max=2)
    pSTransTime : FloatProperty(name="Swim Transition Time", description="Speed of transition between hover and swim in seconds", default=0.2, min=0, max=2)
    pPecOffset : FloatProperty(name="Pectoral Offset", description="Adjustment to allow for different rest pose angles of the fins", default=20.0, min=-90.0, max=90.0)
    pHoverDist : FloatProperty(name="Hover Distance", description="Distance from Target to begin Hover in lengths of the target box. A value of 0 will disable hovering, and the action will be similar to the shark rig.", default=1.0, min=-1.0, max=10.0)
    pHoverTailFrc : FloatProperty(name="Hover Tail Fraction", description="During Hover, the amount of swimming tail movement to retain. 1.0 is full movment, 0 is none", default=0.2, min=0.0, max=5.0)
    pHoverMaxForce : FloatProperty(name="Hover Max Force", description="The maximum force the fins can apply in Hover Mode. 1.0 is quite fast", default=0.2, min=0.0, max=10.0)
    pHoverDerate : FloatProperty(name="Hover Derate", description="In hover, the fish can't go backwards or sideways as fast. This parameter determines how much slower. 1.0 is the same.", default=0.2, min=-0.0, max=1.0)
    pHoverTilt : FloatProperty(name="Hover Tilt", description="The amount of forward/backward tilt in hover as the fish powers forward and backward. in Degrees and based on Max Hover Force", default=4.0, min=-0.0, max=40.0)
    pPecDuration : FloatProperty(name="Pec Duration", description="The amount of hovering the fish can do before a rest. Duration in frames", default=50.0, min=-5.0)
    pPecDuty : FloatProperty(name="Pec Duty Cycle", description="The amount of rest time compared to active time. 1.0 is 50/50, 0.0 is no rest", default=0.8, min=0.0)
    pPecTransition : FloatProperty(name="Pec Transition to rest speed", description="The speed that the pecs change between rest and flap - 1 is instant, 0.05 is fairly slow", default=0.05, min=0.0, max=1.0)
    pHoverTwitch : FloatProperty(name="Hover Twitch", description="The size of twitching while in hover mode in degrees", default=4.0, min=0.0, max=60.0)
    pHoverTwitchTime : FloatProperty(name="Hover Twitch Time", description="The time between twitching while in hover mode in frames", default=40.0, min=0.0)
    pPecSynch : BoolProperty(name="Pec Synch", description="If true then fins beat together, otherwise fins act out of phase", default=False)
    
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
    #pecs
    sPecFinTopL = None
    sPecFinTopR = None
    sPecFinBottomL = None
    sPecFinBottomR = None
    sPecFinPalmL = None
    sPecFinPalmR = None
    sState = 0.0
    sPecState = 0.0
    sPec_scale = 1.0
    sAngularForceV = 0.0
    sTargetProxy = None
    rMaxTailAngle = 0.0
    rMaxFreq = 0.0
    sTargetRig = None
    sOldRqdEffort = 0.0
    sOld_back_fin = None
    sArmatures = []
    nArmature = 0
    sHoverMode = 1.0
    sHoverTurn = 0.0
    sRestFrame = 0.0
    sRestartFrame = 0.0
    sRestAmount = 0.0
    sGoldfish = True
    sStartAngle = 0.0
    sTwitchFrame = 0.0
    sTwitchAngle = 0.0
    sTwitchTarget = 0.0
    
    def SetInitialKeyframe(self, TargetRig, nFrame):
        TargetRig.keyframe_insert(data_path='location',  frame=(nFrame))
        TargetRig.keyframe_insert(data_path='rotation_euler',  frame=(nFrame))
        self.sSpine_master.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        self.sChest.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        self.sTorso.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        self.sBack_fin1.keyframe_insert(data_path='scale',  frame=(nFrame))
        self.sBack_fin2.keyframe_insert(data_path='scale',  frame=(nFrame))
        self.sSideFinL.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        self.sSideFinR.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        self.sSideFinR.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        self.sRoot.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        if self.sGoldfish:
            self.sPecFinPalmL.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
            self.sPecFinPalmR.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
            self.sPecFinTopL.keyframe_insert(data_path='scale',  frame=(nFrame))
            self.sPecFinBottomL.keyframe_insert(data_path='scale',  frame=(nFrame))
            self.sPecFinTopR.keyframe_insert(data_path='scale',  frame=(nFrame))
            self.sPecFinBottomR.keyframe_insert(data_path='scale',  frame=(nFrame))
   
    
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
        #print("Bones:")
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
    def Target(self, TargetRig, TargetProxy, pFS):

        RigDirn = mathutils.Vector((0,-1,0)) @ TargetRig.matrix_world.inverted()
        #print("RigDirn: ", RigDirn)
        
        #distance to target
        if TargetProxy != None:
            TargetDirn = (TargetProxy.matrix_world.to_translation() - TargetRig.location)
            # print("TargetDirn1: ", TargetDirn)
        else:
            TargetDirn = mathutils.Vector((0,-10,0))
            # print("TargetDirn2: ", TargetDirn)
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
        
        #Hover Mode Detection (Close to target and slow)
        if not self.sGoldfish:
            self.sHoverMode = 0.0
        elif TargetDirn.length < (TargetProxy.dimensions[1] * pFS.pHoverDist):# and pFS.sVelocity.length < pFS.pHoverVel:
            self.sHoverMode = min(1.0, self.sHoverMode + pFS.pSTransTime / 25.0)
        else:
            self.sHoverMode = max(0.0, self.sHoverMode - pFS.pHTransTime / 25.0)
        # print("Hover %.2f, %.2f, %.2f, %.2f" % (self.sHoverMode, TargetDirn.length, TargetProxy.dimensions[1] * 3.0, pFS.sVelocity.length))
        
        #Return normalised required effort, turning factor, and ascending factor
        return DifDot,DirectionEffort,DirectionEffortV
        
    #Handle the object movement for swimming
    def ObjectMovment(self, TargetRig, ForwardForce, AngularForce, AngularForceV, nFrame, TargetProxy, pFS):
        # print("MovementSwim")
        #RigDirn = mathutils.Vector((0,-1,0)) * TargetRig.matrix_world.inverted()
        #Total force is tail force - drag
        # DragForce = pFS.pDrag * pFS.sVelocity ** 2.0
        pFS.sVelocity[0] += -(pFS.pDrag * pFS.sVelocity[0] * math.fabs(pFS.sVelocity[0])) / pFS.pMass
        pFS.sVelocity[1] += (-ForwardForce + -pFS.pDrag * pFS.sVelocity[1] * math.fabs(pFS.sVelocity[1])) / pFS.pMass
        pFS.sVelocity[2] += -(pFS.pDrag * pFS.sVelocity[2] * math.fabs(pFS.sVelocity[2])) / pFS.pMass
        # print("Velocity", pFS.sVelocity,pFS.pDrag,pFS.pMass)
        #print("Fwd, Drag: ", ForwardForce, DragForce)
        TargetRig.location += pFS.sVelocity @ TargetRig.matrix_world.inverted()
        TargetRig.keyframe_insert(data_path='location',  frame=(nFrame))
        
        #Let's be simplistic - just rotate object based on angluar force
        TargetRig.rotation_euler.z += math.radians(AngularForce)
        TargetRig.rotation_euler.x += math.radians(AngularForceV)
        TargetRig.keyframe_insert(data_path='rotation_euler',  frame=(nFrame))
        self.sHoverTurn = 0.0
        
        #Forward/Backward Tilt based on force
        if self.sHoverMode <= 0.1:
            self.sRoot.rotation_quaternion = mathutils.Quaternion((1,0,0), math.radians(0))
            self.sRoot.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        
    #Handle the object movement for hovering
    def ObjectMovmentHover(self, TargetRig, nFrame, TargetProxy, pFS):
        # print("MovementHover")
        RigForce = self.sHoverMode * pFS.pPecEffortGain * (TargetProxy.matrix_world.to_translation() - TargetRig.location) @ TargetRig.matrix_world
        
        #Limit the force available
        xHoverMaxForce = pFS.pHoverMaxForce * (1-self.sRestAmount*0.6)
        RigForce[1] = max(RigForce[1], -xHoverMaxForce)
        RigForce[1] = min(RigForce[1], xHoverMaxForce * pFS.pHoverDerate)
        RigForce[2] = max(RigForce[2], -xHoverMaxForce * pFS.pHoverDerate)
        RigForce[2] = min(RigForce[2], xHoverMaxForce * pFS.pHoverDerate)
        RigForce[0] = max(RigForce[0], -xHoverMaxForce * pFS.pHoverDerate)
        RigForce[0] = min(RigForce[0], xHoverMaxForce * pFS.pHoverDerate)

        #Calculate velocity
        pFS.sVelocity[0] += (RigForce[0] - pFS.pDrag * pFS.sVelocity[0] * math.fabs(pFS.sVelocity[0])) / pFS.pMass
        pFS.sVelocity[1] += (RigForce[1] - pFS.pDrag * pFS.sVelocity[1] * math.fabs(pFS.sVelocity[1])) / pFS.pMass
        pFS.sVelocity[2] += (RigForce[2] - pFS.pDrag * pFS.sVelocity[2] * math.fabs(pFS.sVelocity[2])) / pFS.pMass
        TargetRig.location += pFS.sVelocity @ TargetRig.matrix_world.inverted()
        TargetRig.keyframe_insert(data_path='location',  frame=(nFrame))
        # print("sVelocity", pFS.sVelocity)
        
        #Rotate model direction to match target
        # TargetRig.rotation_mode = 'QUATERNION'
        xTargetQuat = TargetProxy.matrix_world.to_quaternion() @ mathutils.Quaternion((0,0,1),math.radians(self.sStartAngle))
        xRigQuat = TargetRig.rotation_euler.to_quaternion()
        xRigQuat = xRigQuat.slerp(xTargetQuat,pFS.pPecTurnAssist/100.0)
        TargetRig.rotation_euler = xRigQuat.to_euler('XYZ', TargetRig.rotation_euler)
        # TargetRig.rotation_mode = 'XYZ'
        TargetRig.keyframe_insert(data_path='rotation_euler',  frame=(nFrame))
        
        #Forward/Backward Tilt based on force
        if RigForce[1] < 0:
            rf = RigForce[1] * pFS.pHoverDerate
        else:
            rf = RigForce[1] 
        TiltAngle = math.radians(pFS.pHoverTilt * rf / (pFS.pHoverMaxForce * pFS.pHoverDerate))
        # self.sRoot.rotation_quaternion = mathutils.Quaternion((-1,0,0), math.radians(0))
        self.sRoot.rotation_quaternion = self.sRoot.rotation_quaternion.slerp(mathutils.Quaternion((1,0,0), TiltAngle),0.03)
        self.sRoot.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        
        #Get left or right turn
        xTurnQuat = TargetRig.rotation_quaternion @ TargetProxy.matrix_world.to_quaternion().inverted()
        self.sHoverTurn = math.degrees(xTurnQuat.to_euler()[2])
        # print("TurnQuat:", self.sHoverTurn)
        
    #Handle the movement of the bones within the armature        
    def BoneMovement(self, context):
    
        
        scene = context.scene
        pFS = scene.FSimProps
        pFSM = scene.FSimMainProps
        startFrame = pFSM.fsim_start_frame
        endFrame = pFSM.fsim_end_frame
        self.sStartAngle = pFSM.fsim_startangle
        
        #Get the current Target Rig
        # try:
        # print("nArmature, sAmartures: ", self.nArmature, self.sArmatures)
        TargetRig = scene.objects.get(self.sArmatures[self.nArmature])
        # except IndexError:
            # TargetRig = None
        self.sTargetRig = TargetRig
    
        #Check the required Rigify bones are present
        self.sRoot = TargetRig.pose.bones.get("root")
        self.sTorso = TargetRig.pose.bones.get("torso")
        self.sSpine_master = TargetRig.pose.bones.get("spine_master")
        if self.sSpine_master is None:
            self.sSpine_master = TargetRig.pose.bones.get("spine_master.002")
        self.sBack_fin1 = TargetRig.pose.bones.get("back_fin_masterBk.001")
        if self.sBack_fin1 is None:
            self.sBack_fin1 = TargetRig.pose.bones.get("back_fin.T.Bk_master")
        self.sBack_fin2 = TargetRig.pose.bones.get("back_fin_masterBk")
        if self.sBack_fin2 is None:
            self.sBack_fin2 = TargetRig.pose.bones.get("back_fin.B.Bk_master")
        self.sBack_fin_middle = TargetRig.pose.bones.get("DEF-back_fin.T.001.Bk")
        self.sChest = TargetRig.pose.bones.get("chest")
        self.sSideFinL = TargetRig.pose.bones.get("side_fin.L")
        self.sSideFinR = TargetRig.pose.bones.get("side_fin.R")
        print("Shark Bone Types:", self.sTorso, self.sChest, self.sBack_fin1, self.sBack_fin2)
        if (self.sSpine_master is None) or (self.sTorso is None) or (self.sChest is None) or (self.sBack_fin1 is None) or (self.sBack_fin2 is None) or (self.sBack_fin_middle is None) or (self.sSideFinL is None) or (self.sSideFinR is None):
            self.report({'ERROR'}, "Sorry, this addon needs a Rigify rig generated from a Shark Metarig")
            print("Not an Suitable Rigify Armature")
            return 0,0
            
        # Pectoral fins if they exist
        self.sPecFinTopL = TargetRig.pose.bones.get("tpec_master.L")
        if self.sPecFinTopL is None:
            self.sPecFinTopL = TargetRig.pose.bones.get("t_master.L")
        self.sPecFinTopR = TargetRig.pose.bones.get("tpec_master.R")
        if self.sPecFinTopR is None:
            self.sPecFinTopR = TargetRig.pose.bones.get("t_master.R")
        self.sPecFinBottomL = TargetRig.pose.bones.get("bpec_master.L")
        if self.sPecFinBottomL is None:
            self.sPecFinBottomL = TargetRig.pose.bones.get("b_master.L")
        self.sPecFinBottomR = TargetRig.pose.bones.get("bpec_master.R")
        if self.sPecFinBottomR is None:
            self.sPecFinBottomR = TargetRig.pose.bones.get("b_master.R")
        self.sPecFinPalmL = TargetRig.pose.bones.get("pec_palm.L")
        self.sPecFinPalmR = TargetRig.pose.bones.get("pec_palm.R")
        if (self.sPecFinTopL is None) or (self.sPecFinTopR is None) or (self.sPecFinBottomL is None) or (self.sPecFinBottomR is None) or (self.sPecFinPalmL is None) or (self.sPecFinPalmR is None):
            print("Not a Goldfish Armature")
            self.sGoldfish = False
            self.sHoverMode = 0.0
            
        #initialise state variabiles
        self.sState = 0.0
        self.AngularForceV = 0.0
        self.sPecState = 0.0
        pFS.sVelocity[0] = pFS.sVelocity[1] = pFS.sVelocity[2] = 0.0
        # print("Init SVelocity", pFS.sVelocity)
            
        #Get TargetProxy object details
        try:
            TargetProxyName = self.sRoot["TargetProxy"]
            # print("TargetProxyName: ", TargetProxyName)
            self.sTargetProxy = bpy.data.objects[TargetProxyName]
        except:
            self.sTargetProxy = None

        print("TargetProxyName: ", self.sTargetProxy.name)
        #Go back to the start before removing keyframes to remember starting point
        context.scene.frame_set(startFrame)
       
        #Delete existing keyframes
        try:
            self.RemoveKeyframes(TargetRig, [self.sSpine_master, self.sBack_fin1, self.sBack_fin2, self.sChest, self.sSideFinL, self.sSideFinR, self.sPecFinPalmL, self.sPecFinPalmR, self.sPecFinTopL, self.sPecFinBottomL, self.sPecFinTopR, self.sPecFinBottomR, self.sRoot, self.sTorso])
        except AttributeError:
            pass
            # print("info: no keyframes")
        
        #record to previous tail position
        context.scene.frame_set(startFrame)
        # context.scene.update()
        self.SetInitialKeyframe(TargetRig, startFrame)
        
        #randomise parameters
        rFact = pFS.pRandom
        self.rMaxTailAngle = pFS.pMaxTailAngle * (1 + (random() * 2.0 - 1.0) * rFact)
        self.rMaxFreq = pFS.pMaxFreq * (1 + (random() * 2.0 - 1.0) * rFact)
        
    def PecSimulation(self, nFrame, pFS, startFrame):
        # print("Pecs")
        if self.sPecFinTopL == None or self.sPecFinTopR == None:
            return
        
        #Update State and main angle
        self.sPecState = self.sPecState + 360.0 / pFS.pMaxPecFreq
        xPecAngle = math.sin(math.radians(self.sPecState))*math.radians(pFS.pMaxPecAngle)
        yPecAngle = math.sin(math.radians(self.sPecState+90.0))*math.radians(pFS.pMaxPecAngle * 2)
        
        #Rest Period Calculations

        if nFrame >= self.sRestartFrame:
            self.sRestAmount = max(0.0, self.sRestAmount - pFS.pPecTransition)
            if self.sRestAmount < 0.1:
                self.sRestFrame = nFrame + pFS.pPecDuration
                self.sRestartFrame = self.sRestFrame + pFS.pPecDuty * pFS.pPecDuration 
            
        if (nFrame >= self.sRestFrame and nFrame < self.sRestartFrame and self.sRestAmount < 1.0):
            self.sRestAmount = min(1.0, self.sRestAmount + pFS.pPecTransition)
            
        # print("RestAmount: ", self.sRestAmount, self.sRestFrame, self.sRestartFrame)
        
        #Add the same side fin wobble to the pec fins to stop them looking boring when not flapping
        SideFinRot = math.radians(math.sin(math.radians(self.sState + pFS.pSideFinPhase)) * pFS.pMaxSideFinAngle)

        #Slerp between oscillating angle and rest angle depending on hover status and reset periods
        # xRestAmount = 1 means no flapping due to either resting or not hovering
        xRestAmount = (1.0 - (1.0 - self.sRestAmount) * self.sHoverMode)
        # print("xRestAmaount: ", xRestAmount)
        # print("RestAmount: ", self.sRestAmount, self.sRestFrame, self.sRestartFrame)
        # print("HoverMode: ", self.sHoverMode)
        yAng = mathutils.Quaternion((0.0, 1.0, 0.0), yPecAngle)
        # yAng = mathutils.Quaternion((0.0, 1.0, 0.0), 0)
        xAng = yAng @ mathutils.Quaternion((1.0, 0.0, 0.0), -xPecAngle)
        xAng = xAng.slerp(mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(pFS.pPecOffset)), xRestAmount)
        self.sPecFinPalmL.rotation_quaternion = xAng @ mathutils.Quaternion((1.0, 0.0, 0.0), SideFinRot)
        self.sPecFinPalmL.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        # print("Palm Animate: ", nFrame)

        #Tip deflection based on phase offset
        xMaxPecScale = pFS.pMaxPecAngle * ( 1.0 / pFS.pPecStiffness) * 0.2 / 30.0
        
        self.sPec_scale = 1.0 + math.sin(math.radians(self.sPecState - pFS.pPecPhase)) * xMaxPecScale * (1.0 - xRestAmount)
        
        self.sPecFinTopL.scale[1] = self.sPec_scale
        self.sPecFinBottomL.scale[1] = 1 - (1 - self.sPec_scale) * pFS.pPecStubRatio
        self.sPecFinTopL.keyframe_insert(data_path='scale',  frame=(nFrame))
        self.sPecFinBottomL.keyframe_insert(data_path='scale',  frame=(nFrame))

        #copy to the right fin
        
        #If fins are opposing
        if not pFS.pPecSynch:
            yAng = mathutils.Quaternion((0.0, 1.0, 0.0), yPecAngle)
            xAng = yAng @ mathutils.Quaternion((1.0, 0.0, 0.0), xPecAngle)
            xAng = xAng.slerp(mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(pFS.pPecOffset)), xRestAmount)
            self.sPecFinPalmR.rotation_quaternion = xAng @ mathutils.Quaternion((1.0, 0.0, 0.0), SideFinRot)
            self.sPecFinTopR.scale[1] = 1/self.sPec_scale
            self.sPecFinBottomR.scale[1] = 1 - (1 - 1/self.sPec_scale) * pFS.pPecStubRatio
        else:
            yAng = mathutils.Quaternion((0.0, 1.0, 0.0), -yPecAngle)
            xAng = yAng @ mathutils.Quaternion((1.0, 0.0, 0.0), -xPecAngle)
            xAng = xAng.slerp(mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(pFS.pPecOffset)), xRestAmount)
            self.sPecFinPalmR.rotation_quaternion = xAng @ mathutils.Quaternion((1.0, 0.0, 0.0), SideFinRot)
            self.sPecFinTopR.scale[1] = self.sPec_scale
            self.sPecFinBottomR.scale[1] = 1 - (1 - self.sPec_scale) * pFS.pPecStubRatio
        self.sPecFinPalmR.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        self.sPecFinTopR.keyframe_insert(data_path='scale',  frame=(nFrame))
        self.sPecFinBottomR.keyframe_insert(data_path='scale',  frame=(nFrame))
        
       
        
    def ModalMove(self, context):
        scene = context.scene
        pFS = scene.FSimProps
        pFSM = scene.FSimMainProps
        startFrame = pFSM.fsim_start_frame
        endFrame = pFSM.fsim_end_frame
        
        nFrame = scene.frame_current
        # print("nFrame: ", nFrame)
        
        
        #Get the effort and direction change to head toward the target
        RqdEffort, RqdDirection, RqdDirectionV = self.Target(self.sTargetRig, self.sTargetProxy, pFS)
        if nFrame == startFrame:
            self.sOldRqdEffort = RqdEffort
            context.scene.frame_set(nFrame + 1)
            self.sOld_back_fin = self.sBack_fin_middle.matrix.decompose()[0]
            return 1
        TargetEffort = pFS.pEffortGain * (pFS.pEffortIntegral * RqdEffort + (RqdEffort - self.sOldRqdEffort))
        self.sOldRqdEffort = RqdEffort
        pFS.sEffort = pFS.pEffortGain * RqdEffort * pFS.pEffortRamp + pFS.sEffort * (1.0-pFS.pEffortRamp)
        pFS.sEffort = min(pFS.sEffort, 1.0)
        #print("Required, Effort:", RqdEffort, pFS.sEffort)
        
        #Pec fin simulation
        self.PecSimulation(nFrame, pFS, startFrame)
        
        #Convert effort into tail frequency and amplitude (Fades to a low value if in hover mode)
        pFS.pFreq = self.rMaxFreq * ((1-self.sHoverMode) * (1.0/(pFS.sEffort+ 0.01)) + self.sHoverMode * 2.0)
        pFS.pTailAngle = self.rMaxTailAngle * ((1-self.sHoverMode) * pFS.sEffort + self.sHoverMode * pFS.pHoverTailFrc)
        #print("rMax, Frc: %.2f, %.2f" % (self.rMaxTailAngle, pFS.pHoverTailFrc))
        
        #Convert direction into Tail Offset angle (Work out swim turn angle and Hover turn angle and mix)
        xSwimTailAngleOffset = RqdDirection * pFS.pMaxSteeringAngle
        xHoverTailAngleOffset = pFS.pMaxSteeringAngle * self.sHoverTurn / 30.0
        xHoverTailAngleOffset = 0.0
        # xHoverFactor = max(0,(1.0 - self.sHoverMode * 4.0))
        pFS.sTailAngleOffset = pFS.sTailAngleOffset * (1 - pFS.pEffortRamp) + pFS.pEffortRamp * max(0,(1.0 - self.sHoverMode*2.0)) * xSwimTailAngleOffset + pFS.pEffortRamp * self.sHoverMode * xHoverTailAngleOffset
        # pFS.sTailAngleOffset = pFS.sTailAngleOffset * (1 - pFS.pEffortRamp) + pFS.pEffortRamp * xSwimTailAngleOffset
        # print("xHoverOffset, TailOffset: ", xHoverTailAngleOffset, pFS.sTailAngleOffset)
        # print("HoverMode, xSwimTailAngleOffset: ", self.sHoverMode, xSwimTailAngleOffset)
        
        #Hover 'Twitch' calculations (Make the fish do some random twisting during hover mode)
        if self.sHoverMode < 0.5:
            #Not hovering so reset
            self.sTwitchTarget = 0.0
            self.sTwitchFrame = 0.0
        else:
            #Hovering, so check if the twitch frame has been reached
            if nFrame >= self.sTwitchFrame:
                #set new twitch frame
                self.sTwitchFrame = nFrame + pFS.pHoverTwitchTime * (random() - 0.5)
                #Only twitch while not resting
                if self.sTwitchFrame < self.sRestartFrame and self.sTwitchFrame > self.sRestFrame:
                    self.sTwitchFrame = self.sRestartFrame + 5
                #set a new twitch target angle
                self.sTwitchTarget = pFS.pHoverTwitch * 2.0 * (random() - 0.5)
        self.sTwitchAngle = self.sTwitchAngle * 0.9 + 0.1 * self.sTwitchTarget
        #print("Twitch Angle: ", self.sTwitchAngle)
            
        
        
        #Spine Movement
        self.sState = self.sState + 360.0 / pFS.pFreq
        xTailAngle = math.sin(math.radians(self.sState))*math.radians(pFS.pTailAngle) + math.radians(pFS.sTailAngleOffset) + math.radians(self.sTwitchAngle)
        #print("Components: %.2f, %.2f, %.2f" % (math.sin(math.radians(self.sState))*math.radians(pFS.pTailAngle),math.radians(pFS.sTailAngleOffset),math.radians(self.sTwitchAngle)))
        #print("TailAngle", math.degrees(xTailAngle))
        self.sSpine_master.rotation_quaternion = mathutils.Quaternion((0.0, 0.0, 1.0), xTailAngle)
        self.sSpine_master.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        ChestRot = mathutils.Quaternion((0.0, 0.0, 1.0), -xTailAngle * pFS.pChestRatio)# - math.radians(pFS.sTailAngleOffset))
        self.sChest.rotation_quaternion = ChestRot @ mathutils.Quaternion((1.0, 0.0, 0.0), -math.fabs(math.radians(pFS.sTailAngleOffset))*pFS.pChestRaise * (1.0 - self.sHoverMode))
        #print("Torso:", pFS.sTailAngleOffset)
        self.sTorso.rotation_quaternion = mathutils.Quaternion((0.0, 1.0, 0.0), -math.radians(pFS.sTailAngleOffset)*pFS.pLeanIntoTurn * (1.0 - self.sHoverMode))
        self.sChest.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        self.sTorso.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        #context.scene.update()
        
        # #Tail Movment
        if (nFrame == startFrame):
            back_fin_dif = 0
        else:
            back_fin_dif = (self.sBack_fin_middle.matrix.decompose()[0].x - self.sOld_back_fin.x)
        self.sOld_back_fin = self.sBack_fin_middle.matrix.decompose()[0]
        
        #Tailfin bending based on phase offset
        pMaxTailScale = pFS.pMaxTailFinAngle * ( 1.0 / pFS.pTailFinStiffness) * 0.2 / 30.0
        
        self.sBack_fin1_scale = 1.0 + math.sin(math.radians(self.sState + pFS.pTailFinPhase)) * pMaxTailScale * (pFS.pTailAngle / self.rMaxTailAngle)
        # print("Bend Factor: ", (pFS.pTailAngle / self.rMaxTailAngle))
        
        self.sBack_fin1.scale[1] = self.sBack_fin1_scale
        self.sBack_fin2.scale[1] = 1 - (1 - self.sBack_fin1_scale) * pFS.pTailFinStubRatio
        self.sBack_fin1.keyframe_insert(data_path='scale',  frame=(nFrame))
        self.sBack_fin2.keyframe_insert(data_path='scale',  frame=(nFrame))
        
        
        SideFinRot = math.sin(math.radians(self.sState + pFS.pSideFinPhase)) * pFS.pMaxSideFinAngle
        
       
        self.sSideFinL.rotation_quaternion = mathutils.Quaternion((1,0,0), math.radians(-SideFinRot))
        self.sSideFinR.rotation_quaternion = mathutils.Quaternion((1,0,0), math.radians(SideFinRot))
       
        self.sSideFinL.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        self.sSideFinR.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        
        #Do Object movment with Forward force and Angular force
        TailFinAngle = (self.sBack_fin1_scale - 1.0) * 30.0 / 0.4
        TailFinAngleForce = math.sin(math.radians(TailFinAngle))
        # ForwardForce = -back_fin_dif * TailFinAngleForce * pFS.pPower
        ForwardForce =  math.fabs(math.cos(math.radians(self.sState))) * math.radians(pFS.pTailAngle) * 15.0 * pFS.pPower / pFS.pMaxFreq
        # print("Force", ForwardForce, math.fabs(math.cos(math.radians(self.sState))), math.radians(pFS.pTailAngle))
        
        #Angular force due to 'swish'
        AngularForce = back_fin_dif  / pFS.pAngularDrag
        
        #Angular force due to rudder effect
        AngularForce += xTailAngle * pFS.sVelocity[1] / pFS.pAngularDrag
        
        #Fake Angular force to make turning more effective
        AngularForce += -(pFS.sTailAngleOffset/pFS.pMaxSteeringAngle) * pFS.pTurnAssist
        
        #Angular force for vertical movement
        self.sAngularForceV = self.sAngularForceV * (1 - pFS.pEffortRamp) + RqdDirectionV * pFS.pMaxVerticalAngle
        
        
        #print("TailFinAngle, AngularForce", xTailAngle, AngularForce)
        if self.sHoverMode < 0.1:
            self.ObjectMovment(self.sTargetRig, ForwardForce, AngularForce, self.sAngularForceV, nFrame, self.sTargetProxy, pFS)
        else:
            self.ObjectMovmentHover(self.sTargetRig, nFrame, self.sTargetProxy, pFS)
        
        
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
                # print("nArmature:", self.nArmature)
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
        # print("Power", context.scene.FSimProps.pPower)
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
        self._timer = wm.event_timer_add(0.001, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


#Register
        
classes = (
    FSimProps,
    ARMATURE_OT_FSimulate,
)

def registerTypes():
    from bpy.utils import register_class

    # Classes.
    for cls in classes:
        register_class(cls)
    # bpy.utils.register_class(FSimProps)
    bpy.types.Scene.FSimProps = bpy.props.PointerProperty(type=FSimProps)
    # bpy.utils.register_class(ARMATURE_OT_FSimulate)

def unregisterTypes():
    from bpy.utils import unregister_class

    del bpy.types.Scene.FSimProps

    # Classes.
    for cls in classes:
        unregister_class(cls)
    # bpy.utils.unregister_class(FSimProps)
    # bpy.utils.unregister_class(ARMATURE_OT_FSimulate)


if __name__ == "__main__":
    register()

