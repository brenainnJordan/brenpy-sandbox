'''Convenience methods for reading and exporting fbx files.

Created on 28 May 2019

@author: Bren
'''

import os
import fbx

from brenpy.utils import io_utils
reload(io_utils)


def get_fbx_ascii_writer_id(fbx_manager):
    """
    Taken from FbxCommon.

    Depending on plugins loaded, fbx ascii could have a different id.

    Find the first fbx format that contains the string "ascii"
    in it's description.

    """

    # registry object holding information about how to read and write files
    io_plugin_registry = fbx_manager.GetIOPluginRegistry()

    # search for fbx ascii writer and return id
    format_count = io_plugin_registry.GetWriterFormatCount()

    for i in range(format_count):
        if io_plugin_registry.WriterIsFBX(i):

            lDesc = io_plugin_registry.GetWriterFormatDescription(i)

            if "ascii" in lDesc:
                return i

    # -1 indicates default writer should be used
    return -1


class BasicIOSettings(object):
    """Set and apply basic IO import/export settings.

    https://help.autodesk.com/view/FBX/2017/ENU/?guid=__cpp_ref_fbxiosettingspath_8h_html

    """

    # EXP_FBX_COLLAPSE_EXTERNALS
    # EXP_FBX_COMPRESS_ARRAYS
    # EXP_FBX_COMPRESS_LEVEL
    # EXP_FBX_COMPRESS_MINSIZE
    # EXP_FBX_EMBEDDED_PROPERTIES_SKIP
    # EXP_FBX_EXPORT_FILE_VERSION
    # EXP_FBX_GLOBAL_SETTINGS
    # EXP_FBX_GOBO
    # EXP_FBX_PASSWORD
    # EXP_FBX_PASSWORD_ENABLE
    # EXP_FBX_TEMPLATE

    def __init__(self):
        self.materials = True
        self.textures = True
        self.embed_media = False
        self.shapes = True
        self.animation = True
        self.characters = True
        self.constraints = True
        self.models = True
        self.pivots = True

#     @classmethod
    def Create(self, fbx_manager, ios_root):
        settings = fbx.FbxIOSettings.Create(
            fbx_manager, fbx.IOSROOT
        )

        for enum_id, value in [
            (fbx.EXP_FBX_MATERIAL, self.materials),
            (fbx.EXP_FBX_TEXTURE, self.textures),
            (fbx.EXP_FBX_EMBEDDED, self.embed_media),
            (fbx.EXP_FBX_SHAPE, self.shapes),
            (fbx.EXP_FBX_ANIMATION, self.animation),
            (fbx.EXP_FBX_CHARACTER, self.characters),
            (fbx.EXP_FBX_CONSTRAINT, self.constraints),
            (fbx.EXP_FBX_MODEL, self.models),
            (fbx.EXP_FBX_PIVOT, self.pivots),
        ]:
            settings.SetBoolProp(enum_id, value)

        return settings

    @staticmethod
    def list_enums():
        """Return a list of all available fbx export setting enum names.
        """
        enums = []
        for i in dir(fbx):
            if i.startswith("EXP_"):
                enums.append(i)
        return enums


def export_scene(
    fbx_manager,
    scene,
    filepath,
    settings=None,
    ascii=True,
    overwrite=False,
    makedirs=False,
    verbose=True,
    err=True
):
    """Export fbx file for specified scene.
    TODO make class and inherit from io_utils class to get validation stuff
    """

    # validate filepath
    if not io_utils.validate_file_write(
        filepath,
        overwrite=overwrite,
        makedirs=makedirs,
        verbose=verbose,
        err=err
    ):
        msg = "Failed to export file: {}".format(filepath)

        if err:
            raise IOError(msg)
        else:
            print msg
            return False

    # format export settings
    if settings:
        if isinstance(settings, BasicIOSettings):

            settings = settings.Create(fbx_manager, fbx.IOSROOT)

        elif not isinstance(settings, fbx.FbxIOSettings):
            raise Exception(
                "Settings must be of type either: {} or {}".format(
                    type(fbx.FbxIOSettings),
                    type(BasicIOSettings)
                )
            )
    else:
        # create default settings
        settings = fbx.FbxIOSettings.Create(
            fbx_manager, fbx.IOSROOT
        )

    fbx_manager.SetIOSettings(settings)

    # get format

    format_id = -1  # default binary

    if ascii:
        if settings.GetBoolProp(fbx.EXP_FBX_EMBEDDED, True):
            raise Exception(
                "Embed media can only be enabled for fbx binary files."
            )

        format_id = get_fbx_ascii_writer_id(fbx_manager)

    # create exporter
    exporter = fbx.FbxExporter.Create(fbx_manager, "")

    # initialize
    try:
        exporter.Initialize(
            filepath, format_id, fbx_manager.GetIOSettings()
        )

    except Exception as err:
        msg = "Call to FbxExporter::Initialize() failed.\n"
        msg += "Error returned: {0}".format(
            exporter.GetStatus().GetErrorString()
        )
        print msg
        raise err

    # export file
    exporter.Export(scene)

    # cleanup
    exporter.Destroy()

    return True


def load_file(
    filepath,
    fbx_manager=None,
    settings=None,
    verbose=True,
    err=True
):
    """Convinience method for loading fbx file.
    """

    # validate filepath
    if not io_utils.validate_file_open(
        filepath,
        verbose=verbose,
        err=err
    ):
        msg = "Failed to load file: {}".format(filepath)

        if err:
            raise IOError(msg)
        else:
            print msg
            return False

    # validate fbx manager
    if fbx_manager is None:
        fbx_manager = fbx.FbxManager.Create()

    # format export settings
    if settings:
        if isinstance(settings, BasicIOSettings):

            settings = settings.Create(fbx_manager, fbx.IOSROOT)

        elif not isinstance(settings, fbx.FbxIOSettings):
            raise Exception(
                "Settings must be of type either: {} or {}".format(
                    type(fbx.FbxIOSettings),
                    type(BasicIOSettings)
                )
            )
    else:
        # create default settings
        settings = fbx.FbxIOSettings.Create(
            fbx_manager, fbx.IOSROOT
        )

    # apply settings
    fbx_manager.SetIOSettings(settings)

    # create importer
    fbx_importer = fbx.FbxImporter.Create(fbx_manager, "")

    # Use the first argument as the filename for the importer.
    try:
        fbx_importer.Initialize(
            filepath, -1, fbx_manager.GetIOSettings()
        )
    except Exception as err:
        msg = "Call to FbxImporter::Initialize() failed.\n"
        msg += "Error returned: {0}".format(
            fbx_importer.GetStatus().GetErrorString()
        )
        print msg
        raise err

    # create scene
    scene_name = os.path.basename(filepath).split(".")[0]
    fbx_scene = fbx.FbxScene.Create(fbx_manager, scene_name)

    # import data
    fbx_importer.Import(fbx_scene)
    fbx_importer.Destroy()

    return fbx_scene, fbx_manager


def test_export():
    """
    TODO test exporting (or not exporting) constraints.
    """
    fbx_manager = fbx.FbxManager()
    scene = fbx.FbxScene.Create(fbx_manager, "testscene")

    settings = BasicIOSettings()
    settings.constraints = False

    export_scene(
        fbx_manager,
        scene,
        r"D:\Repos\dataDump\brenrig\fbx_ascii_test_002.fbx",
        settings=settings,
        ascii=True
    )


if __name__ == "__main__":
    test_export()
