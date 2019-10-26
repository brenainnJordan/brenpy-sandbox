'''
Created on 21 Mar 2019

@author: Bren

TODO find way around missing python event classes.

FbxEmitter
FbxListener
FbxEventHandler


Problem:

fbx python has no concept of Qt-style "signals".

Meaning if something changes in the scene, say the value of a property,
we have no mechanism to automatically update objects that reference
that property.


Solution 1:

We could implement our own signals by subclassing fbx classes
and sending out signals before and after set() method calls.

However this would only serve our own interaction,
if anything else in the fbx scene interacts with an object
no signal will be sent.

Solution 1a:

We build our own fbx python sdk from the C++ source, with this in mind.

Is this even possible?


Solution 2:

The only realistic option is to have a reliable awareness of how changing one object
could change what other objects and update the appropriate references.

For example, say we have two FbxNode objects, one constrained to the other,
and Qt data models referencing both. From a qt widget we set the translation
of the source node. Because we know this will affect the constrained node,
we know that we need to send a signal to the widget referencing the constrained node
to update it's data.

 
What does this mean for our Qt structure?

There should be enough data in the FbxScene to create a mapping that represents
how data flows through the scene, and mimic this in the Qt models.

The exception to this is if FbxObjects are created or destroyed,
however this seems unlikely if not impossible for something in the scene
to trigger this by itself. TODO check this.

So provided that we limit the creation and destruction of objects through
our own classes (maybe some subclassing is neccesary?) we can keep track
of this reliably, and send out signals.



'''

import fbx
import FbxCommon

f_man = fbx.FbxManager()

f_scene = fbx.FbxScene.Create(f_man, "testScene")

root = f_scene.GetRootNode()

test_node = fbx.FbxNode.Create(f_scene, "test_node")

root.AddChild(test_node)

# print test_node.LclTranslation.Get()

# print help(fbx.FbxEventDT)


fbx.FbxNameHandler

for i in dir(fbx.FbxObject.Create(f_man, "sgef")):
    pass
#     print i

test_dbl_prop = fbx.FbxProperty.Create(
    test_node, fbx.FbxDoubleDT, "testDoubleProperty"
)

test_dbl_prop.ModifyFlag(fbx.FbxPropertyFlags.eUserDefined, True)
test_dbl_prop.ModifyFlag(fbx.FbxPropertyFlags.eAnimatable, True)

print test_dbl_prop.Set(16.0)

for i in dir(FbxCommon):
    pass
#     print i

import sys
import pydoc
filepath = r"C:\Users\Bren\Desktop\tests\fbx_help.txt"
f = open(filepath, 'w')
sys.stdout = f
pydoc.help(fbx)
f.close()
sys.stdout = sys.__stdout__

#
# listener.Bind(
#     test_node,
#     fbx
# )
