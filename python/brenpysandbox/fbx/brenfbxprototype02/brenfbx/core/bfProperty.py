'''FbxProperty function set and core subclasses.

Created on 3 Aug 2019

@author: Bren

TODO rethink "input" classes?
Maybe they can be kept, but only as an implied relationship,
to suggest what an object is expecting, however behaviour cannot be enforced.

Needs some restructuring.

'''

from types import NoneType

import fbx

from brenfbx.core import bfData
from brenfbx.core import bfCore
from brenfbx.utils import bfFbxUtils


class BFbxProperty(object):
    """Function set class, akin to Maya "Fn" classes.

    Wraps a FbxProperty object and provides additional functionality.

    DATA_TYPE:
        either None to accept a property with any data type
        or fbx.FbxDataType object to only accept properties of that data type

    TODO allow for child properties

    """

    DATA_TYPE = None

    def __init__(self, fbx_property):
        #         if self.DATA_TYPE is None:
        #             # attempt to cast property
        #             try:
        #                 pass
        #             except:
        #                 raise Exception(
        #                     "Cannot instance class with DATA_TYPE set to None"
        #                 )

        if type(fbx_property) is not fbx.FbxProperty:
            raise Exception(
                "Cannot initialize property function set from type: {}".format(
                    type(fbx_property)
                )
            )

        super(BFbxProperty, self).__init__()

        self._property = fbx_property

        # attempt to cast property
        self._property_class = bfData.get_property_class(fbx_property)

        if self._property_class is None:
            # TODO something! or errors!
            self._cast_property = None
        else:
            self._cast_property = self._property_class(fbx_property)

        # check property is valid
        self.IsValid()

    def log(self, msg):
        """TODO proper logging.
        """
        print msg

    def Property(self):
        return self._property

    def PropertyClass(self):
        return self._property_class

    def CastProperty(self):
        return self._cast_property

    def IsValid(self):
        if self._property_class is None:
            return False

        if self.DATA_TYPE is not None:
            if self._property.GetPropertyDataType() != self.DATA_TYPE:
                self.log(
                    "Property data type ({}) does not match expected data type ({})".format(
                        self._property.GetPropertyDataType().GetName(),
                        self.DATA_TYPE.GetName()
                    )
                )
                return False

        return True

    def Get(self):
        return self._cast_property.Get()

    def Set(self, value):
        # TODO errors?!
        return self._cast_property.Set(value)

    def GetName(self):
        name = self._cast_property.GetName()
        return name

    def GetTypeStr(self):
        return bfFbxUtils.get_property_type_str(self._property)

    @classmethod
    def Create(cls, fbx_object, data_type, name):
        """Create new property and wrap in new instance of cls.
        """
        if cls.DATA_TYPE is not None:
            if data_type is not cls.DATA_TYPE:
                raise Exception(
                    "data type does not match BFbxProperty.DATA_TYPE ({})".format(
                        data_type
                    )
                )

        fbx_property = fbx.FbxProperty.Create(
            fbx_object, data_type, name
        )

        fbx_property.ModifyFlag(
            fbx.FbxPropertyFlags.eUserDefined, True)

        return cls(fbx_property)

    @classmethod
    def CreateFrom(cls):
        """
        TODO Create property as child of another property

        FbxProperty.CreateFrom(
            const FbxProperty & pCompoundProperty, 
            FbxProperty & pFromProperty, 
            bool pCheckForDup = true 
        )

        """
        pass


class IOProperty(BFbxProperty):
    """TODO

    Accepts input property function set of same data type
    and can act as output.

    If connected, Get() will instead call Get() of source property function set.
    We can construct recursive connections via this manner.

    TODO cycle checks before calling Get() to avoid infinite loops.

    """
    pass


class InputPropertyProperty(BFbxProperty):
    """TODO
    Explicit property fn to handle input properties.
    Think of better name?!
    or just use above fn.
    """
    pass


class InputReferenceProperty(BFbxProperty):
    """Property Function set to enforce certain behaviour.

    Property type: fbx.eFbxReference, fbx.FbxReferenceDT

    Property accepts only one source connection and no destination connections.

    TODO create base class, something like ObjectReferenceProperty?

    """

    DATA_TYPE = fbx.FbxReferenceDT
    REFERENCE_TYPES = NoneType

    def __init__(self, fbx_property):
        super(InputReferenceProperty, self).__init__(fbx_property)

    def _make_valid(self):
        """Disconnect destination objects?
        """
        pass

    def IsValid(self):
        """Check connected object is correct type.
        """
        if not super(InputReferenceProperty, self).IsValid():
            return False

        if self.InputExists():
            if not isinstance(
                self.Get(), self.REFERENCE_TYPES
            ):
                self.log("Connected object incorrect type: {}".format(
                    type(self.Get())))
                return False

        return True

    def InputExists(self):
        """
        TODO pass in criteria
        """
        if self._property.GetSrcObjectCount() > 0:
            return True

        return False

    def Get(self):
        """Override default Get behaviour and return connected object.
        """
        if not self.InputExists():
            return None

        return self._property.GetSrcObject(0)

    def Set(self, value):
        """Disconnect old object from property and connect new object.
        """

        if not isinstance(
            value, self.REFERENCE_TYPES
        ):
            raise bfCore.BfError(
                "Input value must be of type: {}, not: {}".format(
                    self.REFERENCE_TYPES,
                    type(value)
                )
            )

        # disconnect existing input node
        self._property.DisconnectAllSrcObject()

        # connect new destination
        if value is None:
            return

        self._property.ConnectSrcObject(value)


class InputReferenceArrayProperty(BFbxProperty):
    """Manages multiple objects to be connected to property.

    TODO refactor names from input to object?

    """

    DATA_TYPE = fbx.FbxReferenceDT
    REFERENCE_TYPES = NoneType

    def __init__(self, fbx_property):
        super(InputReferenceArrayProperty, self).__init__(fbx_property)

    def AddInput(self, input_object):
        """
        """

        if input_object is None:
            return

        if not self.IsValid():
            raise Exception("Class is not valid, cannot add input")

        if not isinstance(
            input_object, self.REFERENCE_TYPES
        ):
            raise bfCore.BfError(
                "Input object must be of type: {}, not: {}".format(
                    self.REFERENCE_TYPES,
                    type(input_object)
                )
            )

#         self._property.ConnectSrcObject(value)

        # check destination is not already connected
        if self._property.IsConnectedDstObject(
            input_object
        ):
            # TODO is an error neccesary?
            raise bfCore.BfError(
                "Input object already connected: {}".format(
                    input_object.GetName())
            )

        # connect destination to property
        self._property.ConnectSrcObject(input_object)

        return True

    def AddInputs(self, input_objects):
        """TODO check stuff.
        """
        for input_object in input_objects:
            self.AddInput(input_object)

        return True

    def RemoveInput(self, input_object):
        # check destination is not already connected
        if not self._property.IsConnectedDstObject(
            input_object
        ):
            # TODO format message depending on object type
            raise bfCore.BfError(
                "Input object is not connected: {}".format(
                    input_object.GetName())
            )

        # disconnect
        self._property.DisonnectSrcObject(input_object)

        return True

    def GetInputs(self):
        """Return all connected objects.
        """

        return [
            self._property.GetSrcObject(i)
            for i in range(
                self._property.GetSrcObjectCount()
            )
        ]

    def InputCount(self):
        return self._property.GetSrcObjectCount()

    def GetInput(self, object_index):
        """
        TODO pass in criteria
        """
        if not self.InputExists(object_index):
            return None

        return self._property.GetSrcObject(object_index)

    def SetInput(self, input_object, object_index):
        """Set input object at given index.

        Fbx provides no mechanism for this,
        so we first need to create a temporary list of connected objects,
        disconnect from property, edit the list, then reconnect.
        """

        # if index is greater than input count
        # we can simply append
        if object_index > self.InputCount():
            return self.AddInput(input_object)

        # TODO maybe insert at zero instead?
        if object_index < 0:
            object_index = 0

        # set input at given index
        temp_input_list = self.GetInputs()

        self._property.DisconnectAllSrcObject()

        temp_input_list[object_index] = input_object

        for _input_object in temp_input_list:
            self.AddInput(_input_object)

        return True

    def InsertInput(self, input_object, object_index):
        """TODO"""
        pass

    def GetInputFromUID(self, unique_id):
        for fbx_object in self.GetInputs():
            if fbx_object.GetUniqueID() == unique_id:
                return fbx_object
        return None

    def InputsExist(self):
        """
        TODO pass in criteria
        """
        if self._property.GetSrcObjectCount() > 0:
            return True

    def InputExists(self, object_index):
        """
        TODO pass in criteria
        """
        if self._property.GetSrcObjectCount() > object_index:
            return True
        else:
            return False

    def ContainsInput(self, input_object):
        return self._property.IsConnectedSrcObject(input_object)


class InputObjectProperty(InputReferenceProperty):
    """Property reference that only accepts incoming connection from FbxObject.
    """
    REFERENCE_TYPES = (fbx.FbxObject, NoneType)

    def __init__(self, *args, **kwargs):
        super(InputObjectProperty, self).__init__(*args, **kwargs)


class InputNodeProperty(InputReferenceProperty):
    """Property reference that only accepts incoming connection from FbxNode.
    """
    REFERENCE_TYPES = (fbx.FbxNode, NoneType)

    def __init__(self, *args, **kwargs):
        super(InputNodeProperty, self).__init__(*args, **kwargs)


class InputObjectArrayProperty(InputReferenceArrayProperty):
    """Property reference that only accepts incoming connection from FbxObject.
    """
    REFERENCE_TYPES = (fbx.FbxObject, NoneType)

    def __init__(self, *args, **kwargs):
        super(InputObjectArrayProperty, self).__init__(*args, **kwargs)


class InputNodeArrayProperty(InputReferenceArrayProperty):
    """Property reference that only accepts incoming connection from FbxNode.
    """
    REFERENCE_TYPES = (fbx.FbxNode, NoneType)

    def __init__(self, *args, **kwargs):
        super(InputNodeArrayProperty, self).__init__(*args, **kwargs)


class FSDouble3Property(BFbxProperty):
    """Property reference that only accepts incoming connection from FbxNode.
    """

    DATA = fbx.FbxDouble3DT

    def __init__(self, *args, **kwargs):
        super(FSDouble3Property, self).__init__(*args, **kwargs)

    def Get(self):
        return self._cast_property.Get()

    def Set(self, value):
        if isinstance(value, (list, tuple)):
            value = fbx.FbxDouble3(*value[:3])

        return self._cast_property.Set(value)


class FSEnumProperty(BFbxProperty):
    """Property Function set to enforce certain behaviour.

    Property type: fbx.eFbxEnum, fbx.FbxEnumDT

    Enum property to choose from predefined list names and corresponding values.

    TODO: allow for backwards compatibility
    eg. if enums are added to at a later date and a file is loaded with older enum.

    TODO: integrate better with native fbxProperty enum methods
          note that property only supports str enum values
          function set allows better duality with arbitrary values
          along with descriptive names.

    """

    DATA_TYPE = fbx.FbxEnumDT

    ENUM_NAMES = []
    ENUM_VALUES = []

    def __init__(self, fbx_property):
        # check class is valid
        if len(self.ENUM_NAMES) != len(self.ENUM_VALUES):
            raise Exception("Class error, inconsistent enum names/values.")

        # TODO check names are unique
        # TODO check values are unique
        # TODO put class validation stuff into classmethod

        super(FSEnumProperty, self).__init__(fbx_property)

    def IsValid(self):

        if self._property.GetEnumCount() != len(self.ENUM_NAMES):
            self.log(
                "Enum count invalid"
            )
            return False

        for i, name in enumerate(self.ENUM_NAMES):
            if self._property.GetEnumValue(i) != name:
                self.log(
                    "Enum name invalid: {} {} {}".format(
                        i, name, self._property.GetEnumValue(i)
                    )
                )
                return False

        if not BFbxProperty.IsValid(self):
            return False

        return True

    def Get(self):
        """TODO fbxProperty.GetEnumValue()?
        """
        enum_index = self._cast_property.Get()
        return self.ENUM_VALUES[enum_index]

    def GetStr(self):
        """TODO fbxProperty.GetEnumValue()?
        """
        enum_index = self._cast_property.Get()
        return self.ENUM_NAMES[enum_index]

    def GetIndex(self):
        """TODO rename GetCurrentIndex?
        """
        enum_index = self._cast_property.Get()
        return enum_index

    def Set(self, value):
        if value in self.ENUM_VALUES:
            enum_index = self.ENUM_VALUES.index(value)
        elif value in self.ENUM_NAMES:
            enum_index = self.ENUM_NAMES.index(value)
        else:
            raise bfCore.BfError(
                "value not recognized, must be either fbx.eEuler enum or name: {}".format(value))

        res = self._cast_property.Set(enum_index)
        return res

    @classmethod
    def Create(cls, fbx_object, data_type, name):
        """Create new property and wrap in new instance of cls.
        """
        if data_type is not cls.DATA_TYPE:
            raise Exception(
                "data type does not match BFbxProperty.DATA_TYPE ({})".format(
                    data_type
                )
            )

        fbx_property = fbx.FbxProperty.Create(
            fbx_object, data_type, name
        )

        fbx_property.ModifyFlag(
            fbx.FbxPropertyFlags.eUserDefined, True)

        # add enums
        for name in cls.ENUM_NAMES:
            fbx_property.AddEnumValue(name)

        return cls(fbx_property)


class FSRotateOrderProperty(FSEnumProperty):
    """Property Function set to enforce certain behaviour.

    Property type: fbx.eFbxEnum, fbx.FbxEnumDT

    Enum property to choose from predefined list of rotation orders.

    """

    ENUM_NAMES = [
        "XYZ",
        "YZX",
        "ZXY",
        "XZY",
        "YXZ",
        "ZYX",
    ]

    ENUM_VALUES = [
        fbx.eEulerXYZ,
        fbx.eEulerYZX,
        fbx.eEulerZXY,
        fbx.eEulerXZY,
        fbx.eEulerYXZ,
        fbx.eEulerZYX,
    ]

    def __init__(self, fbx_property):
        super(FSRotateOrderProperty, self).__init__(fbx_property)


class FSUpTypeProperty(FSEnumProperty):
    """Property Function set to enforce certain behaviour.

    Property type: fbx.eFbxEnum, fbx.FbxEnumDT

    Enum property to choose from predefined list of up types

    """

    ENUM_NAMES = [
        "scene",
        "object",
        "objectRotation",
        "vector",
    ]

    ENUM_VALUES = [
        fbx.FbxConstraintAim.eAimAtSceneUp,
        fbx.FbxConstraintAim.eAimAtObjectUp,
        fbx.FbxConstraintAim.eAimAtObjectRotationUp,
        fbx.FbxConstraintAim.eAimAtVector,
        #         fbx.eAimAtNone, # TODO??? see maya aimConstraint docs
        #         fbx.eAimAtCount
    ]

    def __init__(self, fbx_property):
        super(FSUpTypeProperty, self).__init__(fbx_property)


if __name__ == "__main__":
    pass
