'''FbxObject function set and core sub classes.

Created on 3 Aug 2019

@author: Bren
'''

from types import NoneType

import fbx
import inspect

from brenfbx.core import bfCore
from brenfbx.utils import bfFbxUtils
from brenfbx.fbxsdk.core import bfProperty


class BFbxObject(object):
    """Function set class, akin to Maya "Fn" classes.

    This class does not serialize or deserialize as such.

    However it can create a preconfigured FbxObject
    with specific properties.

    TODO implement GetSrcConnections(primary=True)
         to help build cleaner scene object hierarchy

    """

#     PROPERTY_ARGS = []

    def __init__(self, fbx_object):
        super(BFbxObject, self).__init__()

        # validate args
        if type(fbx_object) is not fbx.FbxObject:
            raise Exception(
                "Cannot initialize BFbxObject from type: {}".format(type(fbx_object)))

        # bind object
        self._object = fbx_object

        self._initialized_properties = []
        self._property_fn_list = []

    @classmethod
    def log(cls, msg, err=False):
        if err:
            raise bfCore.BfError(msg)
        else:
            print msg

    def _initialize_property(
        self, name, data_type, fn_cls=None, default_value=None
    ):
        """Look for expected guide property and create if it doesn't exist.

        name: str
        fbx_type: EFbxType enum (eg. fbx.eFbxReference)
        data_type: FbxDataType enum (eg. fbx.FbxReferenceDT)
        default_value: (property setable type)

        """
        case_sensitive = True

        fbx_property = self._object.FindProperty(name, case_sensitive)

        # check property is expected type
        if fbx_property.IsValid():
            if fbx_property.GetPropertyDataType() != data_type:
                self.log(
                    "Property data type ({}) does not match expected data type ({})".format(
                        fbx_property.GetPropertyDataType().GetName(),
                        data_type.GetName()
                    ),
                    err=True
                )
                return False

            if fbx_property in self._initialized_properties:
                self.log(
                    "Property already initialized! {}".format(
                        fbx_property.GetName()
                    ),
                    err=True
                )

            # wrap property in "FunctionSet" class
            if fn_cls is not None:
                property_fn = fn_cls(fbx_property)
            else:
                property_fn = bfProperty.BfProperty(fbx_property)

        else:
            # if property does not exist, create property with default
            # value
            if fn_cls is not None:
                property_fn = fn_cls.Create(
                    self._object, data_type, name
                )
            else:
                property_fn = bfProperty.BfProperty.Create(
                    self._object, data_type, name
                )

            if default_value is not None:
                property_fn.Set(default_value)

        self._property_fn_list.append(property_fn)
        self._initialized_properties.append(fbx_property)

        return property_fn

    def Object(self):
        """Return bound fbx.FbxObject.
        """
        return self._object

    def PropertyFnList(self):
        return self._property_fn_list

    def IsValid(self):
        """Return if the function set class and instance is valid.
        TODO checks
        """
        for prop in self._property_fn_list:
            if not prop.IsValid():
                self.log("Property not valid: {}".format(prop.GetName()))
                return False

        return True

    def Scene(self):
        return self._object.GetScene()

    def GetName(self):
        return self._object.GetName()

    def SetName(self, value):
        return self._object.SetName(value)

    def GetUniqueID(self):
        return self._object.GetUniqueID()

    @classmethod
    def Create(cls, arg1, name, **kwargs):

        # TODO check args
        # arg1 is either fbx_manager or container

        if "scene" in kwargs.keys():
            fbx_scene = kwargs.pop("scene")
        else:
            fbx_scene = None

        # create empty object
        fbx_object = fbx.FbxObject.Create(arg1, name)

        # connect object to scene
        if fbx_scene is not None:
            fbx_scene.ConnectSrcObject(fbx_object)

        # return new instance of this class
        try:
            obj = cls(fbx_object)
            return obj
        except:
            msg = "ERROR: failed to cast object: {}.{} {}".format(
                inspect.getmodule(cls).__name__, cls.__name__,
                name
            )

            cls.log(msg)

            raise

    def Destroy(self):

        self._initialized_properties = None
        self._property_fn_list = None
        self._object.Destroy()
        self._object = None


class BFbxNode(BFbxObject):
    """TODO"""

    def __init__(self, fbx_object):
        super(BFbxNode, self).__init__(fbx_object)

    def SetName(self, name):
        """TODO rename node attribute
        """
        pass

    def Destroy(self):
        """TODO recursively destroy children
        maybe provide option to reparent instead?
        delete attr?
        print whatever extra we destroy
        """
        pass


class FbxDeferredEvaluator(BFbxObject):
    """Class that can evaluate an operation at a later time.

    TODO use this as base class for modifier class.

    TODO implement something similar to brType property
    so we can find our way back to this class/subclass later.

    """

    def __init__(self, fbx_object):
        super(FbxDeferredEvaluator, self).__init__(fbx_object)

    def IsEvaluateValid(self):
        """Return if the class is ready to evaluate.
        """

        if not self.IsValid():
            self.log("Class is not valid.")
            return False

        return True

    def Evaluate(self):
        if not self.IsEvaluateValid():
            raise Exception(
                "Object is not valid, cannot evaluate: {} ({})".format(
                    self.GetName(), self.__class__.__name__
                )
            )

        return True


class FbxObjectModifier(FbxDeferredEvaluator):
    """
    Specific properties act as inputs
    to allow the class to operate on connected
    destination fbx object via the Evaluate method.
    """

#     DESTINATION_TYPES = (fbx.FbxObject, NoneType)

#     PROPERTY_ARGS = FbxDeferredEvaluator.PROPERTY_ARGS + [
#         ("destination", bfProperty.InputObjectProperty, None)
#     ]

    def __init__(self, fbx_object):
        super(FbxObjectModifier, self).__init__(fbx_object)

        # initialize expected properties
#         self._destination_property = self._initialize_property(
#             "destination", fbx.eFbxReference, fbx.FbxReferenceDT, default_value=None
#         )
#         self.Destination = self._initialize_property(
#             "destination", fbx.FbxReferenceDT, default_value=None,
#         )

        # TODO replace destination methods with property fn methods
        self.Destination = self._initialize_property(
            "destination", fbx.FbxReferenceDT, default_value=None,
            fn_cls=bfProperty.InputObjectProperty
        )
#
#     def SetDestination(self, destination):
#
#         if not isinstance(
#             destination, self.DESTINATION_TYPES
#         ):
#             raise Exception(
#                 "Destination must be or type: {}".format(
#                     self.DESTINATION_TYPES
#                 )
#             )
#
#         # disconnect existing destination
#         if self.DestinationExists():
#             current_scene = self._object.GetScene()
#
#             if current_scene is not None:
#                 self._object.DisconnectDstObject(current_scene)
#
#             if self._object.IsConnectedDstObject(
#                 self.GetDestination()
#             ):
#                 self._object.DisconnectDstObject(
#                     self.GetDestination()
#                 )
#
# #         self._destination_property.DisconnectAllSrcObject()
#         self.Destination.Property().DisconnectAllSrcObject()
#
#         # connect new destination
#         if destination is None:
#             return
#
#         # attach bound object to same scene as destination
#         # TODO should this even be an option?
#         # should we enforce objects are bound to one scene only?
#         destination_scene = destination.GetScene()
#
#         if destination_scene is None:
#             raise Exception(
#                 "Destination object is not attached to a FbxScene: {}".format(
#                     destination)
#             )
#
#         self._object.ConnectDstObject(destination_scene)
#
#         # connect destination to property
#         self.Destination.Property().ConnectSrcObject(destination)
#
#     def GetDestination(self):
#         """
#         TODO pass in criteria
#         """
#         if not self.DestinationExists():
#             return None
#
# #         return self._destination_property.GetSrcObject(0)
#         return self.Destination.Property().GetSrcObject(0)
#
#     def DestinationExists(self):
#         """
#         TODO pass in criteria
#         """
# #         if self._destination_property.GetSrcObjectCount() > 0:
#         if self.Destination.Property().GetSrcObjectCount() > 0:
#             return True

    def IsValid(self):
        """Return if the class is valid.
        """
        return FbxDeferredEvaluator.IsValid(self)

    def IsEvaluateValid(self):
        """Return if the class is ready to evaluate.
        """
        # TODO check properties are all valid
        # TODO check bound object still exists
        # TODO check bound object is valid
        # TODO validate destination objects are correct type and can be
        # modified
        if not FbxDeferredEvaluator.IsEvaluateValid(self):
            return False

#         if not self.DestinationExists():
#             self.log("Destination does not exist")
#             return False

        if not self.Destination.InputExists():
            self.log("Destination does not exist")
            return False

        return True

    def Evaluate(self):
        res = FbxDeferredEvaluator.Evaluate(self)

        return True


class FbxObjectMultModifierOld(FbxDeferredEvaluator):
    """Deferred evaluator that can act on multiple destination objects.
    """

    DESTINATION_TYPES = (fbx.FbxObject, NoneType)

    def __init__(self, fbx_object):
        super(FbxObjectMultModifier, self).__init__(fbx_object)

        self.Destinations = self._initialize_property(
            "destinations", fbx.FbxReferenceDT, default_value=None,
        )

    def AddDestination(self, destination):

        if not self.IsValid():
            raise Exception("Class is not valid, cannot add Destination")

        # allow for passing in function sets
        if isinstance(destination, BFbxObject):
            destination = destination.Object()

        # check type
        if not isinstance(
            destination, self.DESTINATION_TYPES
        ):
            raise Exception(
                "Destination must be or type: {}".format(
                    self.DESTINATION_TYPES
                )
            )

        # check destination is not already connected
        if self.Destinations.Property().IsConnectedDstObject(
            destination
        ):
            # TODO is an error neccesary?
            # TODO custom exception to allow catching
            raise Exception(
                "Destination already connected: {}".format(destination))

        # sync scenes
        # skip for now
        # TODO is it actually neccessary to enforce this?
        if False:
            current_scene = self._object.GetScene()
            destination_scene = destination.GetScene()

            if destination_scene is None:
                raise Exception(
                    "Destination object is not attached to a FbxScene: {} ({})".format(
                        destination.GetName(), destination
                    )
                )

            elif self.DestinationsExist():
                # check destination exists in the same scene as bound object
                if destination_scene != current_scene:
                    raise Exception(
                        "Destination object is not attached to same FbxScene as bound object: {}".format(
                            destination)
                    )
            else:
                # attach bound object to new scene
                if current_scene is not None:
                    self._object.DisconnectSrcObject(current_scene)

                self._object.ConnectDstObject(destination_scene)

        # connect destination to property
        self.Destinations.Property().ConnectSrcObject(destination)

        return True

    def AddDestinations(self, destinations):
        """TODO check stuff.
        """
        for destination in destinations:
            self.AddDestination(destination)

        return True

    def RemoveDestination(self, destination):
        # check destination is not already connected
        if not self.Destinations.Property().IsConnectedDstObject(
            destination
        ):
            raise Exception(
                "Destination is not connected: {}".format(destination))

        # disconnect
        self.Destinations.Property().DisonnectSrcObject(destination)

        return True

    def GetDestinations(self):
        """Get all connected destination objects of destination property.
        """
        dst_prop = self.Destinations.Property()

        destinations = [
            dst_prop.GetSrcObject(i)
            for i in range(
                dst_prop.GetSrcObjectCount()
            )
        ]

        return destinations

    def GetDestination(self, dst_index):
        """
        TODO pass in criteria
        """
        if not self.DestinationExists(dst_index):
            return None

        return self.Destinations.Property().GetSrcObject(dst_index)

    def DestinationsExist(self):
        """
        TODO pass in criteria
        """
        if self.Destinations.Property().GetSrcObjectCount() > 0:
            return True

    def DestinationExists(self, dst_index):
        """
        TODO pass in criteria
        """
        if self.Destination.Property().GetSrcObjectCount() > dst_index:
            return True

    def IsValid(self):
        """Return if the class is valid.
        """
        # TODO check all destination objects are in the same scene
        if not FbxDeferredEvaluator.IsValid(self):
            return False

        current_scene = self._object.GetScene()

        if self.DestinationsExist() and current_scene is None:
            # if object is not attached to a scene then something's gone wrong!
            # TODO should this actually be enforced?
            # or is a warning enough?
            # are there any scenarios where we would want to use a destination
            # from a different scene?
            raise Exception(
                "Internal error: Bound object is not attached to a FbxScene"
            )

        return True

    def IsEvaluateValid(self):
        """Return if the class is ready to evaluate.
        """
        # TODO check properties are all valid
        # TODO check bound object still exists
        # TODO check bound object is valid
        # TODO validate destination objects are correct type and can be
        # modified
        if not FbxDeferredEvaluator.IsEvaluateValid(self):
            return False

        if not self.DestinationsExist():
            self.log("Destinations do not exist")
            return False

        return True

    def Evaluate(self):
        res = FbxDeferredEvaluator.Evaluate(self)

        return True


class FbxObjectMultModifier(FbxDeferredEvaluator):
    """Deferred evaluator that can act on multiple destination objects.
    """

    def __init__(self, fbx_object):
        super(FbxObjectMultModifier, self).__init__(fbx_object)

        self.Destinations = self._initialize_property(
            "destinations",
            fbx.FbxReferenceDT,
            fn_cls=bfProperty.InputObjectArrayProperty,
            default_value=None,
        )

    def IsValid(self):
        """Return if the class is valid.
        """
        # TODO check all destination objects are in the same scene
        if not FbxDeferredEvaluator.IsValid(self):
            return False

        current_scene = self._object.GetScene()

        if self.Destinations.InputsExist() and current_scene is None:
            # if object is not attached to a scene then something's gone wrong!
            # TODO should this actually be enforced?
            # or is a warning enough?
            # are there any scenarios where we would want to use a destination
            # from a different scene?
            raise Exception(
                "Internal error: Bound object is not attached to a FbxScene"
            )

        return True

    def IsEvaluateValid(self):
        """Return if the class is ready to evaluate.
        """
        # TODO check properties are all valid
        # TODO check bound object still exists
        # TODO check bound object is valid
        # TODO validate destination objects are correct type and can be
        # modified
        if not FbxDeferredEvaluator.IsEvaluateValid(self):
            return False

        if not self.Destinations.InputsExist():
            self.log("Destinations do not exist")
            return False

        return True

    def Evaluate(self):
        res = FbxDeferredEvaluator.Evaluate(self)

        return True


class FbxNodeMultModifier(FbxDeferredEvaluator):
    """Deferred evaluator that can act on multiple destination nodes.
    """

    def __init__(self, fbx_object):
        super(FbxNodeMultModifier, self).__init__(fbx_object)

        self.Destinations = self._initialize_property(
            "destinations",
            fbx.FbxReferenceDT,
            fn_cls=bfProperty.InputNodeArrayProperty,
            default_value=None,
        )

    def IsValid(self):
        """Return if the class is valid.
        """
        # TODO check all destination objects are in the same scene
        if not FbxDeferredEvaluator.IsValid(self):
            return False

        current_scene = self._object.GetScene()

        if self.Destinations.InputsExist() and current_scene is None:
            # if object is not attached to a scene then something's gone wrong!
            # TODO should this actually be enforced?
            # or is a warning enough?
            # are there any scenarios where we would want to use a destination
            # from a different scene?
            raise Exception(
                "Internal error: Bound object is not attached to a FbxScene"
            )

        return True

    def IsEvaluateValid(self):
        """Return if the class is ready to evaluate.
        """
        # TODO check properties are all valid
        # TODO check bound object still exists
        # TODO check bound object is valid
        # TODO validate destination objects are correct type and can be
        # modified
        if not FbxDeferredEvaluator.IsEvaluateValid(self):
            return False

        if not self.Destinations.InputsExist():
            self.log("Destinations do not exist")
            return False

        return True

    def Evaluate(self):
        res = FbxDeferredEvaluator.Evaluate(self)

        return True


class MMdEvaluator(FbxObjectMultModifier):
    """Custom class to evaluate br objects.

    "MMd" indicates this is a mult modifier subclass.

    destination br types are all classes that have an Evaluate method.

    TODO consider refactoring this to inherit from DefferedEvaluator

    then objectMultModifier could inherit from this instead,
    with destination_br_base_classes set to (something?)

    TODO rework "br types" to however we implement evaluator type property.
    """

    DESTINATION_TYPES = (fbx.FbxObject, NoneType)

    DESTINATION_BR_BASE_CLASSES = (
        #         fbx_modifier_prototype_003.FbxObjectModifier,
    )

    def __init__(self, fbx_object):
        super(MMdEvaluator, self).__init__(fbx_object)

    def AddDestination(self, destination):
        # allow for passing in function sets
        if isinstance(destination, BFbxObject):
            fbx_object = destination.Object()
        else:
            fbx_object = destination

        # get brType
        cls = bfFbxUtils.get_br_type_cls(fbx_object, err=True, verbose=True)

        # check class matches destination base class types
        if not issubclass(cls, self.DESTINATION_BR_BASE_CLASSES):
            raise Exception(
                "Desination object ({}) brType must be subclass of one of the following: {}".format(
                    cls.__name__, self.DESTINATION_BR_BASE_CLASSES
                )
            )

        # if checks pass then we can add!
#         super(MMdEvaluator, self).AddDestination(destination)
        self.Destinations.AddInput(fbx_object)

        return True

    def AddDestinations(self, destinations):
        """TODO check stuff.
        """
        for destination in destinations:
            self.AddDestination(destination)

        return True

    def IsValid(self):
        """
        TODO check all destination objects are subclasses of FbxObjectModifier.
        """
        res = super(MMdEvaluator, self).IsValid()

        return res

    def Evaluate(self):
        """Wrap each destination in corresponding function set class and evaluate.
        """
        res = super(MMdEvaluator, self).Evaluate()

#         for destination in self.GetDestinations():
        for destination in self.Destinations.GetInputs():

            fn_cls = bfFbxUtils.get_br_type_cls(
                destination, err=True, verbose=True
            )

            fn_object = fn_cls(destination)
            fn_object.Evaluate()

        return True


class MMdModifierEvaluator(MMdEvaluator):
    """Custom class to evaluate modifier objects.

    "MMd" indicates this is a mult modifier subclass.

    Redundant??
    """

    DESTINATION_BR_BASE_CLASSES = (
        FbxObjectModifier,
    )

    def __init__(self, fbx_object):
        super(MMdModifierEvaluator, self).__init__(fbx_object)


class FbxNodeModifier(FbxDeferredEvaluator):
    """
    Specific properties act as inputs
    to allow the class to operate on connected
    destination fbx object via the Evaluate method.
    """

#     DESTINATION_TYPES = (fbx.FbxNode, NoneType)

    def __init__(self, fbx_object):
        super(FbxNodeModifier, self).__init__(fbx_object)

        self.Destination = self._initialize_property(
            "destination", fbx.FbxReferenceDT, default_value=None,
            fn_cls=bfProperty.InputNodeProperty
        )

    def IsEvaluateValid(self):
        """Return if the class is ready to evaluate.
        """
        # TODO check properties are all valid
        # TODO check bound object still exists
        # TODO check bound object is valid
        # TODO validate destination objects are correct type and can be
        # modified
        if not FbxDeferredEvaluator.IsEvaluateValid(self):
            return False

        if not self.Destination.InputExists():
            self.log("Destination does not exist")
            return False

        return True


class FbxPropertyModifier(FbxDeferredEvaluator):
    """
    Specific properties act as inputs
    to allow the class to operate on connected
    destination fbx property via the Evaluate method.

    TODO

    TODO add some property specific stuff,
    like methods to get and set destination property etc.
    or getting destination property type.

    """

    def __init__(self, fbx_object):
        super(FbxPropertyModifier, self).__init__(fbx_object)

        # initialize expected properties
        # TODO
#         self._destination_property = self._initialize_property(
#             "destination", fbx.eFbxReference, fbx.FbxReferenceDT, default_value=None
#         )


class BrObjectArrayOld(BFbxObject):
    """Fbx object specifically for holding an array of br objects.

    Can have properties of it's own.

    """

    def __init__(self, fbx_object):
        super(BrObjectArray, self).__init__(fbx_object)

        # TODO replace with InputReferenceArrayProperty
        self._br_objects_property = self._initialize_property(
            "brObjects", fbx.FbxReferenceDT, default_value=None,
        )

    def add_object(self, br_object):
        """Connect fbx object to object and property.
        TODO check if already connected.
        TODO add permisable list of object types we can add.
        TODO allow passing in br_objects of fbx_objects
        """
        if self._br_objects_property.Property().IsConnectedSrcObject(br_object):
            print "warning fbx object already connected to array, skipping: {}".format(
                br_object.GetName()
            )

        self._br_objects_property.Property().ConnectSrcObject(br_object)

        for fbx_object in self.Scene(), self.Object():
            if not fbx_object.IsConnectedSrcObject(br_object):
                fbx_object.ConnectSrcObject(br_object)

    def remove_object(self, session_object):
        """
        TODO
        """
        pass

    def contains_object(self, session_object):
        pass

    def GetObjectCount(self):
        return self._br_objects_property.Property().GetSrcObjectCount()

    def GetObject(self, object_index, wrap=True):
        """
        """
        fbx_object = self._br_objects_property.Property().GetSrcObject(object_index)

        if fbx_object is None:
            return None

        if wrap:
            fn_cls = bfFbxUtils.get_br_type_cls(
                fbx_object, err=False, verbose=False)

            if fn_cls is None:
                return fbx_object

            # TODO validate fn_cls is modifier
            try:
                print "BLAH ", fn_cls, fbx_object.GetName()
                return fn_cls(fbx_object)
            except:
                print "BLAH ", fn_cls, fbx_object.GetName()
                print "BLAH POOP ", fn_cls.__bases__[0].__bases__
                raise
        else:

            return fbx_object

    def GetObjects(self, wrap=True):
        """Get joint nodes from guides property.
        """
        src_count = self._br_objects_property.Property().GetSrcObjectCount()

        fbx_objects = []

        for i in range(src_count):
            fbx_object = self.GetObject(i, wrap=wrap)
            fbx_objects.append(fbx_object)

        return fbx_objects

    def GetObjectFromUID(self, unique_id):
        """Find br object with matching unique ID.
        """
        src_count = self._br_objects_property.Property().GetSrcObjectCount()

        for i in range(src_count):
            fbx_object = self.GetObject(i, wrap=False)
            if fbx_object.GetUniqueID() == unique_id:
                return fbx_object

        return None


class BrObjectArray(BFbxObject):
    """Fbx object specifically for holding an array of br objects.

    Can have properties of it's own.

    """

    def __init__(self, fbx_object):
        super(BrObjectArray, self).__init__(fbx_object)

        # TODO replace with InputReferenceArrayProperty

        # TODO prevent user from editing this property manually
        # or provide stronger typing

        self.BrObjects = self._initialize_property(
            "brObjects",
            fbx.FbxReferenceDT,
            fn_cls=bfProperty.InputObjectArrayProperty,
            default_value=None,
        )

    def add_object(self, br_object):
        """Connect fbx object to object and property.
        TODO check if already connected.
        TODO add permisable list of object types we can add.
        TODO allow passing in br_objects of fbx_objects
        """

        if isinstance(br_object, BFbxObject):
            br_object = br_object.Object()

        if self.BrObjects.ContainsInput(br_object):
            print "warning fbx object already connected to array, skipping: {}".format(
                br_object.GetName()
            )

        self.BrObjects.AddInput(br_object)

        if False:
            # skip scene connections
            # TODO give warning if scenes do not match (in property fn?)
            for fbx_object in self.Scene(), self.Object():
                if not fbx_object.IsConnectedSrcObject(br_object):
                    fbx_object.ConnectSrcObject(br_object)

    def remove_object(self, br_object):
        """
        TODO
        """
        if isinstance(br_object, BFbxObject):
            br_object = br_object.Object()

        self.BrObjects.RemoveInput(br_object)

    def contains_object(self, br_object):
        if isinstance(br_object, BFbxObject):
            br_object = br_object.Object()

        return self.BrObjects.ContainsInput(br_object)

    def GetObjectCount(self):
        return self.BrObjects.InputCount()

    def GetObject(self, object_index, wrap=True):
        """
        """
        fbx_object = self.BrObjects.GetInput(object_index)

        if fbx_object is None:
            return None

        if wrap:
            fn_cls = bfFbxUtils.get_br_type_cls(
                fbx_object, err=False, verbose=False)

            if fn_cls is None:
                return fbx_object

            # TODO validate fn_cls is modifier
            try:
                print "BLAH ", fn_cls, fbx_object.GetName()
                return fn_cls(fbx_object)
            except:
                print "BLAH ", fn_cls, fbx_object.GetName()
                print "BLAH POOP ", fn_cls.__bases__[0].__bases__
                raise
        else:

            return fbx_object

    def GetObjects(self, wrap=True):
        """Get joint nodes from guides property.
        """

        fbx_objects = []

        for i in range(self.GetObjectCount()):
            fbx_object = self.GetObject(i, wrap=wrap)
            fbx_objects.append(fbx_object)

        return fbx_objects

    def GetObjectFromUID(self, unique_id):
        """Find br object with matching unique ID.
        TODO wrap?
        """
        return self.BrObjects.GetInputFromUID(unique_id)


class BrNodeArray(BrObjectArray):
    """Fbx object specifically for holding an array of br nodes.

    Can have properties of it's own.

    Supports node hierarchys

    Object holds it's own RootNode (FbxNode) which is protected (TODO)

    The idea being that the RootNode is never a part of another hierarchy,
    similar to FbxScene (how do we enforce this?)

    TODO is this flawed?

    An array suggests a list of nodes, with no enforced relationship.

    What we want instead is maybe a "RootNode" function set,
    that implies that it shouldn't be parented to other stuff.

    """

    def __init__(self, fbx_object):
        super(BrNodeArray, self).__init__(fbx_object)

        self._root_node_property = self._initialize_property(
            "rootNode", fbx.FbxReferenceDT, default_value=None,
            fn_cls=bfProperty.InputNodeProperty
        )

    @classmethod
    def Create(cls, *args, **kwargs):
        """Override Create method to include additional objects.

        """

        # parse args
        # manager could either be FbxManager or FbxObject (container)
        manager, name = args[:2]

        # create session object as normal
        br_array_object = super(BrNodeArray, cls).Create(*args, **kwargs)

        # create and connect root node
        root_node = fbx.FbxNode.Create(
            manager,
            "{}_rootNode".format(name)
        )

        br_array_object._root_node_property.Set(
            root_node
        )

        return br_array_object

    def GetRootNode(self):
        return self._root_node_property.Get()

    def GetTopNodes(self, wrap=False):
        """Wrap TODO"""
        top_nodes = [
            self.GetRootNode().GetChild(i)
            for i in range(self.GetRootNode().GetChildCount())
        ]

        return top_nodes


class BrRootNode():
    pass
