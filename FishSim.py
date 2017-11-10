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

# version comment: V0.1.1 develop branch - start on pec animation (includes tail angle fix)

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
    pTailFinPhase = FloatProperty(name="Tail Fin Phase", description="Tail Fin phase offset from tail movement in degrees", default=90.0, min=45.0, max=135.0)
    pTailFinStiffness = FloatProperty(name="Tail Fin Stiffness", description="Tail Fin Stiffness", default=1.0, min=0, max=2.0)
    pTailFinStubRatio = FloatProperty(name="Tail Fin Stub Ratio", description="Ratio for the bottom part of the tail", default=0.3, min=0, max=3.0)
    pMaxSideFinAngle = FloatProperty(name="Max Side Fin Angle", description="Max side fin angle", default=5.0, min=0, max=60.0)
    pSideFinPhase = FloatProperty(name="Side Fin Phase", description="Side Fin phase offset from tail movement in degrees", default=90.0, min=45.0, max=135.0)
    # pSideFinStiffness = FloatProperty(name="Side Fin Stiffness", description="Side Fin Stiffness", default=0.2, min=0, max=10.0)
    pChestRatio = FloatProperty(name="Chest Ratio", description="Ratio of the front of the fish to the rear", default=0.5, min=0, max=2.0)
    pChestRaise = FloatProperty(name="Chest Raise Factor", description="Chest raises during turning", default=1.0, min=0, max=20.0)
    pLeanIntoTurn = FloatProperty(name="LeanIntoTurn", description="Amount it leans into the turns", default=1.0, min=0, max=20.0)
    pRandom = FloatProperty(name="Random", description="Random amount", default=0.25, min=0, max=1.0)

    #Pectoral Fin Properties
    pMaxPecFreq = FloatProperty(name="Pectoral Stroke Period", description="Maximum frequency of pectoral fin movement in frames per cycle", default=10.0, min=0)
    pMaxPecAngle = FloatProperty(name="Max Pec Fin Angle", description="Max Pectoral Fin Angle", default=20.0, min=0, max=80)
    pPecPhase = FloatProperty(name="Pec Fin Tip Phase", description="How far the fin tip lags behind the main movement in degrees", default=90.0, min=0, max=180)
    pPecStubRatio = FloatProperty(name="Pectoral Stub Ratio", description="Ratio for the bottom part of the pectoral fin", default=0.7, min=0, max=2)
    pPecStiffness = FloatProperty(name="Pec Fin Stiffness", description="Pectoral fin stiffness, with 1.0 being very stiff", default=0.7, min=0, max=2)
    
    
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
        # try:
        TargetRig = scene.objects.get(self.sArmatures[self.nArmature])
        # except IndexError:
            # TargetRig = None
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
            
        # Pectoral fins if they exist
        self.sPecFinTopL = TargetRig.pose.bones.get("t_master.L")
        self.sPecFinTopR = TargetRig.pose.bones.get("t_master.R")
        self.sPecFinBottomL = TargetRig.pose.bones.get("b_master.L")
        self.sPecFinBottomR = TargetRig.pose.bones.get("b_master.R")
        self.sPecFinPalmL = TargetRig.pose.bones.get("pec_palm.L")
        self.sPecFinPalmR = TargetRig.pose.bones.get("pec_palm.R")
            
        #initialise state variabiles
        self.sState = 0.0
        self.AngularForceV = 0.0
        self.sPecState = 0.0
            
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
        
    def PecSimulation(self, nFrame, pFS):
        print("Pecs")
        if self.sPecFinTopL == None or self.sPecFinTopL == None:
            return
        self.sPecState = self.sPecState + 360.0 / pFS.pMaxPecFreq
        xPecAngle = math.sin(math.radians(self.sPecState))*math.radians(pFS.pMaxPecAngle)
        print("XPecAngle: ", xPecAngle)
        self.sPecFinPalmL.rotation_quaternion = mathutils.Quaternion((1.0, 0.0, 0.0), xPecAngle)
        self.sPecFinPalmL.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        #Tip deflection based on phase offset
        xMaxPecScale = pFS.pMaxPecAngle * ( 1.0 / pFS.pPecStiffness) * 0.2 / 30.0
        
        self.sPec_scale = 1.0 + math.sin(math.radians(self.sPecState - pFS.pPecPhase)) * xMaxPecScale
        
        self.sPecFinTopL.scale[1] = self.sPec_scale
        self.sPecFinBottomL.scale[1] = 1 - (1 - self.sPec_scale) * pFS.pPecStubRatio
        self.sPecFinTopL.keyframe_insert(data_path='scale',  frame=(nFrame))
        self.sPecFinBottomL.keyframe_insert(data_path='scale',  frame=(nFrame))

        #copy to the right fin
        self.sPecFinPalmR.rotation_quaternion = mathutils.Quaternion((1.0, 0.0, 0.0), xPecAngle)
        self.sPecFinPalmR.keyframe_insert(data_path='rotation_quaternion',  frame=(nFrame))
        self.sPecFinTopR.scale[1] = self.sPec_scale
        self.sPecFinBottomR.scale[1] = 1 - (1 - self.sPec_scale) * pFS.pPecStubRatio
        self.sPecFinTopR.keyframe_insert(data_path='scale',  frame=(nFrame))
        self.sPecFinBottomR.keyframe_insert(data_path='scale',  frame=(nFrame))

       
        
    def ModalMove(self, context):
        scene = context.scene
        pFS = scene.FSimProps
        pFSM = scene.FSimMainProps
        startFrame = pFSM.fsim_start_frame
        endFrame = pFSM.fsim_end_frame
        
        nFrame = scene.frame_current
        
        self.PecSimulation(nFrame, pFS)
        
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
        
        #
        # -- Old Tail Section --
        #
        # #Tail Movment
        if (nFrame == startFrame):
            back_fin_dif = 0
        else:
            back_fin_dif = (self.sBack_fin_middle.matrix.decompose()[0].x - self.sOld_back_fin.x)
        self.sOld_back_fin = self.sBack_fin_middle.matrix.decompose()[0]
    
        # #Tail Fin angle based on Tail movement
        # pMaxTailScale = pFS.pMaxTailFinAngle * 0.4 / 30.0
        # currentTailScale = self.sBack_fin1.scale[1]
        # if (back_fin_dif < 0) :
            # TailScaleIncr = (1 + pMaxTailScale - currentTailScale) * pFS.pTailFinGain * math.fabs(back_fin_dif)
            # #print("Positive scale: ", TailScaleIncr)
        # else:
            # TailScaleIncr = (1 - pMaxTailScale - currentTailScale) * pFS.pTailFinGain * math.fabs(back_fin_dif)
            # #print("Negative scale: ", TailScaleIncr)
        
        # #Tail Fin stiffness factor
        # TailFinStiffnessIncr = (1 - currentTailScale) * pFS.pTailFinStiffness
        
        # if (nFrame == startFrame):
            # self.sBack_fin1_scale = 1.0
        # else:
            # self.sBack_fin1_scale = self.sBack_fin1.scale[1] + TailScaleIncr + TailFinStiffnessIncr
            
        # #Limit Tail Fin maximum deflection    
        # if (self.sBack_fin1_scale > (pMaxTailScale + 1)):
            # self.sBack_fin1_scale = pMaxTailScale + 1
        # if (self.sBack_fin1_scale < (-pMaxTailScale + 1)):
            # self.sBack_fin1_scale = -pMaxTailScale + 1
        # self.sBack_fin1.scale[1] = self.sBack_fin1_scale
        # self.sBack_fin2.scale[1] = 1 - (1 - self.sBack_fin1_scale) * pFS.pTailFinStubRatio
        # #scene.update()
        # #print("New Scale:", self.sBack_fin1.scale[1])
        # self.sBack_fin1.keyframe_insert(data_path='scale',  frame=(nFrame))
        # self.sBack_fin2.keyframe_insert(data_path='scale',  frame=(nFrame))
        
        #
        # -- New tail section --
        #
        #Tailfin based on phase offset
        pMaxTailScale = pFS.pMaxTailFinAngle * ( 1.0 / pFS.pTailFinStiffness) * 0.2 / 30.0
        
        self.sBack_fin1_scale = 1.0 + math.sin(math.radians(self.sState + pFS.pTailFinPhase)) * pMaxTailScale
        
        self.sBack_fin1.scale[1] = self.sBack_fin1_scale
        self.sBack_fin2.scale[1] = 1 - (1 - self.sBack_fin1_scale) * pFS.pTailFinStubRatio
        self.sBack_fin1.keyframe_insert(data_path='scale',  frame=(nFrame))
        self.sBack_fin2.keyframe_insert(data_path='scale',  frame=(nFrame))
        
        #
        # -- end tail section --
        #
        
        # #Side Fin angle based on Tail movement
        # pMaxSideFinAngle = pFS.pMaxSideFinAngle
        # currentSideFinRot = math.degrees(self.sSideFinL.rotation_quaternion.to_euler().x)
        # if (back_fin_dif < 0) :
            # SideIncr = (pMaxSideFinAngle - currentSideFinRot) * pFS.pSideFinGain * math.fabs(back_fin_dif)
            # #print("Side Positive scale: ", SideIncr)
        # else:
            # SideIncr = (-pMaxSideFinAngle - currentSideFinRot) * pFS.pSideFinGain * math.fabs(back_fin_dif)
            # #print("Side Negative scale: ", SideIncr)
        
        # #Side Fin stiffness factor
        # SideFinStiffnessIncr = -currentSideFinRot * pFS.pSideFinStiffness
        
        # if (nFrame == startFrame):
            # SideFinRot = 0.0
        # else:
            # SideFinRot = currentSideFinRot + SideIncr + SideFinStiffnessIncr
            # #print("Current, incr, stiff: ", currentSideFinRot, SideIncr, SideFinStiffnessIncr)

        # #Limit Side Fin maximum deflection    
        # if (SideFinRot > pMaxSideFinAngle):
            # SideFinRot = pMaxSideFinAngle
        # if (SideFinRot < -pMaxSideFinAngle):
            # SideFinRot = -pMaxSideFinAngle
            
        #
        # -- New Side fin section
        #
        
        SideFinRot = math.sin(math.radians(self.sState + pFS.pSideFinPhase)) * pFS.pMaxSideFinAngle
        
        #
        # -- End new sidefin section
        #
        
        self.sSideFinL.rotation_quaternion = mathutils.Quaternion((1,0,0), math.radians(-SideFinRot))
        self.sSideFinR.rotation_quaternion = mathutils.Quaternion((1,0,0), math.radians(SideFinRot))
       
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

    # def draw(self, context):
        # pFS = context.scene.FSimProps
        # layout = self.layout
        # layout.operator('screen.repeat_last', text="Repeat", icon='FILE_REFRESH' )
        
        # box = layout.box()
        # box.label("Main Parameters")
        # box.prop(pFS, "pMass")
        # box.prop(pFS, "pDrag")
        # box.prop(pFS, "pPower")
        # box.prop(pFS, "pMaxFreq")
        # box.prop(pFS, "pMaxTailAngle")
        # box = layout.box()
        # box.label("Turning Parameters")
        # box.prop(pFS, "pAngularDrag")
        # box.prop(pFS, "pMaxSteeringAngle")
        # box.prop(pFS, "pTurnAssist")
        # box.prop(pFS, "pLeanIntoTurn")
        # box = layout.box()
        # box.label("Target Tracking")
        # box.prop(pFS, "pEffortGain")
        # box.prop(pFS, "pEffortIntegral")
        # box.prop(pFS, "pEffortRamp")
        # box = layout.box()
        # box.label("Fine Tuning")
        # box.prop(pFS, "pMaxTailFinAngle")
        # box.prop(pFS, "pTailFinGain")
        # box.prop(pFS, "pTailFinStiffness")
        # box.prop(pFS, "pTailFinStubRatio")
        # box.prop(pFS, "pMaxSideFinAngle")
        # box.prop(pFS, "pSideFinGain")
        # box.prop(pFS, "pSideFinStiffness")
        # box.prop(pFS, "pChestRatio")
        # box.prop(pFS, "pChestRaise")
        # box.prop(pFS, "pMaxVerticalAngle")
        # box.prop(pFS, "pRandom")



def registerTypes():
    bpy.utils.register_class(FSimProps)
    bpy.types.Scene.FSimProps = bpy.props.PointerProperty(type=FSimProps)
    bpy.utils.register_class(ARMATURE_OT_FSimulate)

def unregisterTypes():
    del bpy.types.Scene.FSimProps
    bpy.utils.unregister_class(FSimProps)
    bpy.utils.unregister_class(ARMATURE_OT_FSimulate)


if __name__ == "__main__":
    register()

