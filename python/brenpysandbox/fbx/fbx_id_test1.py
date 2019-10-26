'''
Created on 24 Mar 2019

@author: Bren
'''

import fbx
import FbxCommon

f_man = fbx.FbxManager()

f_scene = fbx.FbxScene.Create(f_man, "testScene")

root = f_scene.GetRootNode()

test_node_1 = fbx.FbxNode.Create(f_scene, "test_node1")
root.AddChild(test_node_1)

print test_node_1.GetUniqueID()

test_node_2 = fbx.FbxNode.Create(f_scene, "test_node2")
root.AddChild(test_node_2)

print test_node_1.GetUniqueID()
print test_node_2.GetUniqueID()


also_test_node_1 = root.GetChild(0)
print also_test_node_1.GetUniqueID()

print test_node_1 == also_test_node_1
print test_node_1 is also_test_node_1

print test_node_1
print also_test_node_1

print f_scene.FindNodeByName("test_node1")

print "all nodes:"

for i in range(f_scene.GetNodeCount()):
    node = f_scene.GetNode(i)
    print node, node.GetName(), node.GetUniqueID()


print "delete stuff"

print f_scene.RemoveNode(test_node_1)

for i in range(f_scene.GetNodeCount()):
    node = f_scene.GetNode(i)
    print node, node.GetName(), node.GetUniqueID()

test_node_1 = fbx.FbxNode.Create(f_scene, "test_node1")
root.AddChild(test_node_1)

print test_node_1.GetUniqueID()
