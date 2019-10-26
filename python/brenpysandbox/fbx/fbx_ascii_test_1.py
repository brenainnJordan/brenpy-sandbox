'''
Created on 28 May 2019

@author: Bren
'''

import os
import fbx

DUMP_DIR = r"D:\Repos\dataDump\brenrig"

FILEPATH = os.path.join(
    DUMP_DIR,
    "fbx_ascii_test_001.fbx"
)


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


def export_test_scene():
    fbx_manager = fbx.FbxManager()
    scene = fbx.FbxScene.Create(fbx_manager, "testscene")

    io_settings = fbx.FbxIOSettings.Create(
        fbx_manager, fbx.IOSROOT
    )

    fbx_manager.SetIOSettings(io_settings)

    exporter = fbx.FbxExporter.Create(fbx_manager, "")

    format_id = get_fbx_ascii_writer_id(fbx_manager)
#     format_id = -1 # binary

    try:
        exporter.Initialize(
            FILEPATH, format_id, fbx_manager.GetIOSettings()
        )

    except Exception as err:
        msg = "Call to FbxExporter::Initialize() failed.\n"
        msg += "Error returned: {0}".format(
            exporter.GetStatus().GetErrorString()
        )
        print msg
        raise err

    exporter.Export(scene)
    exporter.Destroy()


if __name__ == "__main__":
    export_test_scene()
