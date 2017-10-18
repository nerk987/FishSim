#FishSim - Blender Fish Swimming Simulator Addon

Stay tuned - the addon is being developed. An alpha version should be available within a few weeks.



Documentation so far...
## Introduction
Most computer animation is done manually by setting keyframes at key points, and then tweaking intermediate frames. For some types of animation however, it should be possible for the computer to do the detail work once the animator has set up the appropriate environment. Bullet physics and the fracture modifier are examples.

This addon aims to make it easier to animate natural movements of fish by allowing the animation of targets or proxies, and then simulating the movements required for the fish to follow these targets. It would be hard to support every type of rig that could be built for a fish model, but the shark metarig supplied with the built-in rigify addon provides a convenient standard that should be easy to apply to most models.

In the real world, fish often come in large numbers. There is already a wonderful addon called Crowdmaster which is designed to move large numbers of objects according to complex stategies.  It's very well suited to setup an initial pattern for a school of fish and then animate the motion according to flocking, path following, object avoiding rules. In fact, it could handle the whole task including specifying armature actions to simulate swimming but the actions would end up somewhat robotic. Instead, it can be used to drive the motion of the targets, and the FishSim addon can then be used to produce realistic swimming physics for the 'actors' to follow the targets.

## Workflow summary
...* Create or download a fish model
...* Use the Rigify Shark metarig to rig the model (or download a rigged model)
...* Install and enable the FishSim addon. The FishSim panel will be available while the fish armature is selected
...* From the FishSim tools panel, add a target for the model
...* Animate the target via keyframes, path follow etc to show the fish model where to swim
...* From the FishSim tools panel, select the range of frames and select 'Simulate'
...* Run the animation (Alt-A), and tweak the simulation parameters to provide the desired swimming action 

The above workflow can be used to animate as many fish models as you like. However, for large numbers, some additional steps can make this easier.

...* Use the workflow above to create a fish model with a FishSim target object.
...* Duplicate and animate the target as many times and with whatever tools you like. The Crowdmaster addon is very suitable, as is the Animation Nodes addon. 
...* Select the 'Copy Rigs' option in the 'Multi Sim Options' box and select the 'Simulate' button to make a copy of the fish armature at every target object location
...* Select the 'Copy Meshes' option in the 'Multi Sim Options' box and select the 'Simulate' button to make a copy of the fish mesh object(s) attached to the armatures at every target object location
...* Select the 'Simulate the multiple rigs' option in the 'Multi Sim Options' box to simulate the swimming action for every amaramture and every target object location.
...* Some of the options above can take a long time, so number a armatures copied and/or simulated can be limited while testing using the 'Maximum number of copies' parameter. 



