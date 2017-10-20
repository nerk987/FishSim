# Introduction
Most computer animation is done manually by setting keyframes at key points, and then tweaking intermediate frames. For some types of animation however, it should be possible for the computer to do the detail work once the animator has set up the appropriate environment. Bullet physics and the fracture modifier are examples.

This addon aims to make it easier to animate natural movements of fish by allowing the animation of targets or proxies, and then simulating the movements required for the fish to follow these targets. It would be hard to support every type of rig that could be built for a fish model, but the shark metarig supplied with the built-in rigify addon provides a convenient standard that should be easy to apply to most models.

In the real world, fish often come in large numbers. There is already an impressive addon called Crowdmaster which is designed to move large numbers of objects according to complex stategies.  It's very well suited to setup an initial pattern for a school of fish and then animate the motion according to flocking, path following, object avoiding rules. In fact, it could handle the whole task including specifying armature actions to simulate swimming but the actions would end up somewhat robotic. Instead, it can be used to drive the motion of the targets, and the FishSim addon can then be used to produce realistic swimming physics for the 'actors' to follow the targets. An example crowdmaster setup suitable for this addon is provided. The 'animation nodes' addon is an alternative.

# Workflow summary
* Create or download a fish model
* Use the Rigify Shark metarig to rig the model (or download one of the example models)
* Install and enable the FishSim addon. The FishSim panel will be available while the fish armature is selected
* From the FishSim tools panel, add a target for the model
* Animate the target via keyframes, path follow etc to show the fish model where to swim
* From the FishSim tools panel, select the range of frames and select 'Simulate'
* Run the animation (Alt-A), and tweak the simulation parameters to provide the desired swimming action 

The above workflow can be used to animate as many fish models as you like. However, for large numbers, some additional steps can make this easier.

* Use the workflow above to create a fish model with a FishSim target object.
* Tweak the simulation parameters to suit the planned speed of the targets.
* Duplicate and animate the target as many times and with whatever tools you like. The Crowdmaster addon is very suitable, as is the Animation Nodes addon. 
* Select the 'Copy Rigs' option in the 'Multi Sim Options' box and select the 'Simulate' button to make a copy of the fish armature at every target object location. Optionally limit the number of rigs to a small number using the 'Maximum number of copies' parameter to speed up the initial testing.
* Select the 'Simulate the multiple rigs' option in the 'Multi Sim Options' box to simulate the swimming action for every amaramture and every target object location. Again tweak the swimming simulation parameters.
* Select the 'Copy Meshes' option (and untick the other options) in the 'Multi Sim Options' box and select the 'Simulate' button to make a copy of the fish mesh object(s) attached to the armatures at every target object location.

# Reference
## Installation
It's like just about every other Blender addon. Download the file here:

From the Blender file menu, choose 'User Preferences'. Switch to the 'Add-ons' tab, then select 'Install Add-on from file'. Browse to the location of the downloaded addon. Enable 'FishSim' from the list of add-ons.

There should be a 'FishSim' tab on the Toolbar to the left of the 3D view whenever an armature is selected in object or pose mode.


## Rigify Shark Metarig

If you haven't used it, Rigify is a hugely powerful rig generator add-on that is supplied with Blender. When enabled, the 'Add Amature' menu is extended to allow the creation of various metarigs. It now supports a 'Shark' metarig, and after you adjust the metarig to suit your model, Rigify can generate a fully functioning control rig. 

The FishSim add-on doesn't need Rigify to be installed to work, but it does expect the rig to have been generated with Rigify from the standard Shark metarig. You can download a shark model rigged in a suitable way from here:  or make your own. Even if you have a model rigged using a different method, it should be quite easy to re-rig it using Rigify.

## FishSim Tools Panel
Once FishSim is loaded and enabled, a panel should appear on the Tool Panel on the left of a 3D view if an armature is slected in Pose or Object mode. 

![alt text](file:///F:/Bentley%20Software/Addons/FishSim/FSim_ToolPanel.png "Tools Panel")

1. Animation Range

>The swimming motion of the fish armatures will be animated by setting keyframes between the 'Simulation Start Frame' and the 'Simulation End Frame'.

2. Add a Target

>The 'Add a Target' button will add a 'Target Proxy' object set to the bounding box size of the armature, and with wire frame display enabled. The idea then is to animate the motion of the Target Proxy, and then the fish armature can be automatically simulated to follow the target. 

>A 'custom property' is added to the root bone of the fish armature so that the fish knows which target to follow. The Target Proxy also gets a custom property to identify it, and this tag includes the first three letters of the rig - we'll mention this later as it helps when you have different types of fish.  






