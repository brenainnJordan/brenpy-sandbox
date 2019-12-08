"""Test utilities to read hit film files.

XML Example Structure...

<BiffProject AppEdition="1000" AppVersion="3.1.5213.10801" CurrentScreen="2">
<Project Version="2">
    <ID>7fa0c08b-7068-40a5-9178-a300568a8dba</ID>
    <Name/>
    <ProjectSettings Version="1">
        <BPC>1000</BPC>
        <AntialiasingMode>1</AntialiasingMode>
    </ProjectSettings>
    <AssetList>
        <Assets>
            <MediaAsset Version="1">
                <ID>fddd956e-803f-4a93-ab00-f8385ebbcc9e</ID>
                <Name>MVI_4165.MOV</Name>
                <ParentFolderID>00000000-0000-0000-0000-000000000000</ParentFolderID>
                <Filename>C:\Partition\Bands\PablosDog\Gigs\160709_hawesBash\hawesBash_2016_video\MVI_4165.MOV</Filename>
                <IsImageSequence>0</IsImageSequence>
                <OverrideFrameRate>0</OverrideFrameRate>
                <FrameRate>30</FrameRate>
                <OverrideFields>0</OverrideFields>
                <Fields>0</Fields>
                <OverridePAR>0</OverridePAR>
                <PAR>0</PAR>
                <OverrideAlpha>0</OverrideAlpha>
                <AlphaMode>0</AlphaMode>
                <InPoint>0</InPoint>
                <OutPoint>1056</OutPoint>
                <Instances>
                    <Instance ID="f2b183eb-1abf-4a36-ba58-e5b9de9d5d2d" Type="1"/>
                    <Instance ID="faa7bfb3-ebb8-43a1-8d26-a1adf653888b" Type="0"/>
                    <Instance ID="53dcceea-a896-4923-955a-29f6ecdbe457" Type="0"/>
                    <Instance ID="aff8147b-b234-4cf8-a472-35671a0ddece" Type="1"/>
                    <Instance ID="228a5e4b-1ff1-48e2-b013-633b8299968c" Type="1"/>
                    <Instance ID="7a2d59dd-1a19-4f65-8e10-f24845cec099" Type="0"/>
                    <Instance ID="bca3a623-762f-4ed4-a4fa-ce2502c74743" Type="0"/>
                    <Instance ID="4356b11e-2c23-4f2f-b933-f5fb8b2cfa17" Type="1"/>
                    <Instance ID="20c3bab8-4a0c-4e51-90fe-58f676234690" Type="0"/>
                    <Instance ID="cafd1ca6-e96c-4196-8386-2c11642b8ddf" Type="1"/>
                    <Instance ID="366ba56e-595b-437c-867b-9874e3060bfc" Type="0"/>
                    <Instance ID="ecd5cee5-2f7c-4b02-8673-cea436ec8027" Type="1"/>
                </Instances>
            </MediaAsset>
        </Assets>
        <BinFolder Version="0">
            <ID>16556e84-3562-4fff-9908-955c21b6ee69</ID>
            <IsExpanded>0</IsExpanded>
            <Name>Root</Name>
            <ParentFolderID>00000000-0000-0000-0000-000000000000</ParentFolderID>
            <Assets>
                <ID>ddfc2282-7b9b-4f63-bbad-2fb9a876baa5</ID>
                <ID>942c4e59-5d0b-4516-bf26-4a09ab3e463c</ID>
                <ID>e7bddca9-7107-4a14-8664-27654f601750</ID>
                ...
            </Assets>
            <SubFolders/>
        </BinFolder>
    </AssetList>
    <EditorSequence>
        <ID>ac16d293-57a7-4ac9-9329-2147c226e3d3</ID>
        <Name>Editor</Name>
        <CTI>21396</CTI>
        <InPoint>15643</InPoint>
        <OutPoint>21524</OutPoint>
        <TimelineZoom>0.05</TimelineZoom>
        <TimelineTimeFormat>1000</TimelineTimeFormat>
        <TimelineSnapMode>1001</TimelineSnapMode>
        <VideoPreviewSize>1001</VideoPreviewSize>
        <AudioPreviewSize>1001</AudioPreviewSize>
        <PreviewMode>1002</PreviewMode>
        <AudioVideoSettings Version="0">
            <FrameCount>34101</FrameCount>
            <AudioSampleRate>48000</AudioSampleRate>
            <Width>1920</Width>
            <Height>1080</Height>
            <Fields>0</Fields>
            <PAR>0</PAR>
            <PARCustom>0</PARCustom>
            <FrameRate>25</FrameRate>
        </AudioVideoSettings>
        <Video>
            <VideoTrack>
                <ID>2913c582-efa1-4afd-bfe3-c4930d548521</ID>
                <Name>Video 1</Name>
                <Visible>1</Visible>
                <Objects>
                    <VisualObject>
                        <ID>bd6ba03f-8e1e-4672-9f82-3b34dd392f3f</ID>
                        <SequenceID>ac16d293-57a7-4ac9-9329-2147c226e3d3</SequenceID>
                        <Name>MVI_4154.MOV</Name>
                        <AssetID>c696ef25-3983-4353-a7a1-37f27cdbaa00</AssetID>
                        <AssetType>0</AssetType>
                        <AssetInstanceStart>3020</AssetInstanceStart>
                        <StartFrame>6809</StartFrame>
                        <EndFrame>6852</EndFrame>
                        <ParentTrackID>139cf815-a989-4ebd-a2c0-8500ffd28380</ParentTrackID>
                        <LinkedObjectID>27403c3c-9f7a-4e32-b159-9dee2d5db55f</LinkedObjectID>
                        <BlendMode>0</BlendMode>
                        <PropertyManager Version="1">
                            <opacity Spatial="0" Type="0">
                                <Default V="3">
                                    <fl>100</fl>
                                </Default>
                            </opacity>
                            <rotationZ Spatial="0" Type="1">
                                <Default V="3">
                                    <fl>0</fl>
                                </Default>
                            </rotationZ>
                            <position Spatial="0" Type="1">
                                <Default V="3">
                                    <p2 X="0" Y="0"/>
                                </Default>
                            </position>
                            <anchorPoint Spatial="0" Type="1">
                                <Default V="3">
                                    <p2 X="0" Y="0"/>
                                </Default>
                            </anchorPoint>
                            <speed Spatial="0" Type="1">
                                <Default V="3">
                                    <db>1</db>
                                </Default>
                            </speed>
                            <scale Spatial="0" Type="1">
                                <Default V="3">
                                    <sc X="100" Y="100" Z="100"/>
                                </Default>
                            </scale>
                            <scaleLinked Spatial="0" Type="1">
                                <Default V="3">
                                    <b>1</b>
                                </Default>
                            </scaleLinked>
                        </PropertyManager>
                        <Effects/>
        <Audio>
            <AudioTrack>
                <ID>1731fd84-bf17-4239-95ec-ae22c19d9b4f</ID>
                <Name>Audio 5</Name>
                <Muted>0</Muted>
                <Level>0</Level>
                <Objects>
                    <AudioObject>
                        <ID>fa45059b-6f9b-4eb2-8def-17200de47502</ID>
                        <SequenceID>ac16d293-57a7-4ac9-9329-2147c226e3d3</SequenceID>
                        <Name>MVI_4164.MOV</Name>
                        <AssetID>17953364-6140-472a-93e6-c75946ab8084</AssetID>
                        <AssetType>0</AssetType>
                        <AssetInstanceStart>337</AssetInstanceStart>
                        <StartFrame>323</StartFrame>
                        <EndFrame>785</EndFrame>
                        <Muted>0</Muted>
                        <ParentTrackID>1e032880-2eb0-4607-b71f-a57c767f05d6</ParentTrackID>
                        <LinkedObjectID>0b59b85a-4a03-4754-aef2-56a1b2461917</LinkedObjectID>
                        <PropertyManager Version="1">
                            <audioLevel Spatial="0" Type="0">
                                <Default V="3">
                                    <fl>0</fl>
                                </Default>
                            </audioLevel>
                            <speed Spatial="0" Type="1">
                                <Default V="3">
                                    <db>1</db>
                                </Default>
                            </speed>
                        </PropertyManager>
                        <Effects/>
                    </AudioObject>
                </Objects>
            </AudioTrack>
        </Audio>
        <ViewerState Version="2">
            <CurrentLayout>0</CurrentLayout>
            <Layout0 Pos0="182a9edd-3850-4e10-a33c-ecb2a4a36dde"/>
            <Layout1/>
            ...
        </ViewerState>
    </EditorSequence>
    <Metadata Version="0">
        <bool>
            <Item K="3475470396" V="1"/>
            ...
    </Metadata>
</Project>

"""

# from dicttoxml import dicttoxml
# import xmltodict
from xml.dom import minidom
import xml.etree.ElementTree as ET
import os
import sys
import re
import pprint
import json

TEST_HF_FILE = r"D:\Bands\PablosDog\Gigs\160709_hawesBash\edit\hawesBash030716_003 - Copy.hfp"
TEST_EDL_FILE = r"D:\Bands\PablosDog\Gigs\160709_hawesBash\edit\hawesBash030716_003_edl_test_01.edl"

def generate_frame_number(hours, minutes, seconds, frames, frame_rate):
    """Calculate frame number using specified timecode and fps
    """
    # check user input
    for name, value in [
        ("hours", hours), ("minutes", minutes), ("seconds", seconds), ("frames", frames), ("frame_rate", frame_rate)
    ]:
        if value < 0:
            raise Exception("{} cannot be less than zero".format(name))

    if frames >= frame_rate:
        raise Exception("frames value must be less than frame rate")
    if seconds >= 60:
        raise Exception("seconds value must be less than 60")
    if minutes >= 60:
        raise Exception("minutes value must be less than 60")


    # calculate frame number
    frame_number = sum([
        frames,
        seconds * frame_rate,
        minutes * 60 * frame_rate,
        hours * 60 * 60 * frame_rate
    ])

    return frame_number


def generate_timecode(frame_number, frame_rate):
    """Calculate timecode using specified frame number and fps.
    """
    frames = frame_number % frame_rate

    remaining_frames = frame_number - frames
    seconds = (remaining_frames / frame_rate) % 60

    remaining_frames -= (seconds * frame_rate)
    minutes = (remaining_frames / frame_rate / 60) % 60

    remaining_frames -= (minutes * 60 * frame_rate)
    hours = remaining_frames / (60 * 60 * frame_rate)

    return [hours, minutes, seconds, frames]

def format_edl_timecode(hours, minutes, seconds, frames):
    tc = [hours, minutes, seconds, frames]
    tc = ["{0:02d}".format(i) for i in tc]
    return ":".join(tc)

class EditObject(object):
    def __init__(self):
        super(EditObject, self).__init__()

    def _repr_attrs(self):
        """Return a list of class attributes to include in __repr__
        """
        return []

    def _repr_text(self, indent_level, text, label=None):
        """Return formatted text including indents and label.
        """
        if label is not None:
            text = "{}: {}".format(label, text)

        text = "{}{}\n".format("\t" * indent_level, text)

        return text

    def _repr_obj(self, indent_level, obj, label=None):
        """Return formatted text appropriate to type of object.
        """
        if isinstance(obj, EditObject):
            return obj.__repr__(label=label, indent_level=indent_level)

        elif isinstance(obj, (list, tuple)):

            text = self._repr_text(indent_level, "", label=label)

            for i, obj_i in enumerate(obj):
                text += self._repr_obj(
                    indent_level + 1,
                    obj_i,
                    label=None,
                )

            return text

        else:

            return self._repr_text(indent_level, obj, label=label)

    def __repr__(self, label=None, indent_level=0):
        """Return pretty print string of edit data.
        """
        # repr = super(HitFilmObject, self).__repr__()
        first_line = "<{} Object>".format(self.__class__.__name__)

        repr = self._repr_text(indent_level, first_line, label=label)

        for attr_name in self._repr_attrs():
            attr_obj = getattr(self, attr_name)

            repr += self._repr_obj(indent_level + 1, attr_obj, label=attr_name)

        return repr


class HitFilmObject(EditObject):
    def __init__(self):
        super(HitFilmObject, self).__init__()
        self.id = None
        self.name = None

    def _repr_attrs(self):
        attrs = super(HitFilmObject, self)._repr_attrs()
        attrs += ["id", "name"]
        return attrs

    def deserialise_xml(self, xml_element):
        self.id = xml_element.find("ID").text
        self.name = xml_element.find("Name").text


class Project(HitFilmObject):
    def __init__(self):
        super(Project, self).__init__()

        self.asset_list = AssetList()
        self.editor_sequence = EditorSequence()

    def _repr_attrs(self):
        attrs = super(Project, self)._repr_attrs()
        attrs += ["asset_list", "editor_sequence"]
        return attrs

    def deserialise_xml(self, xml_element):
        super(Project, self).deserialise_xml(xml_element)

        asset_list_element = xml_element.find("AssetList")
        self.asset_list.deserialise_xml(asset_list_element)

        editor_sequence_list_element = xml_element.find("EditorSequence")
        self.editor_sequence.deserialise_xml(editor_sequence_list_element)


class AssetList(EditObject):
    def __init__(self):
        super(AssetList, self).__init__()

        self.assets = []
        self.bin_folder = BinFolder()

    def _repr_attrs(self):
        attrs = super(AssetList, self)._repr_attrs()
        attrs += ["assets", "bin_folder"]
        return attrs

    def deserialise_xml(self, xml_element):
        # super(AssetList, self).deserialise_xml(xml_element)

        # deserialize assets
        assets_element = xml_element.find("Assets")

        self.assets = []

        for media_asset_element in assets_element.findall("MediaAsset"):
            media_asset = MediaAsset()
            media_asset.deserialise_xml(media_asset_element)
            self.assets.append(media_asset)

        # deserialize bin folder
        bin_folder_element = xml_element.find("BinFolder")
        self.bin_folder.deserialise_xml(bin_folder_element)


class EditorSequence(HitFilmObject):
    def __init__(self):
        super(EditorSequence, self).__init__()
        self.cti = None
        self.in_point = None
        self.out_point = None
        self.timeline_zoom = None
        self.timeline_time_format = None
        self.timeline_snap_mode = None
        self.video_preview_size = None
        self.audio_preview_size = None
        self.preview_mode = None
        self.audio_video_settings = AudioVideoSettings()
        self.video = []
        self.audio = []

    def _repr_attrs(self):
        attrs = super(EditorSequence, self)._repr_attrs()
        attrs += [
            "cti", "in_point", "out_point", "timeline_zoom", "timeline_time_format", "timeline_snap_mode",
            "video_preview_size",
            "audio_preview_size", "preview_mode", "audio_video_settings", "video", "audio"
        ]
        return attrs

    def deserialise_xml(self, xml_element):
        super(EditorSequence, self).deserialise_xml(xml_element)

        self.cti = int(xml_element.find("CTI").text)
        self.in_point = int(xml_element.find("InPoint").text)
        self.out_point = int(xml_element.find("OutPoint").text)
        self.timeline_zoom = float(xml_element.find("TimelineZoom").text)
        self.timeline_time_format = int(xml_element.find("TimelineTimeFormat").text)
        self.timeline_snap_mode = int(xml_element.find("TimelineSnapMode").text)
        self.video_preview_size = int(xml_element.find("VideoPreviewSize").text)
        self.audio_preview_size = int(xml_element.find("AudioPreviewSize").text)
        self.preview_mode = int(xml_element.find("PreviewMode").text)

        self.audio_video_settings.deserialise_xml(
            xml_element.find("AudioVideoSettings")
        )

        self.video = []

        video_element = xml_element.find("Video")

        for video_track_element in video_element.findall("VideoTrack"):
            video_track = VideoTrack()
            video_track.deserialise_xml(video_track_element)
            self.video.append(video_track)

        self.audio = []

        audio_element = xml_element.find("Audio")

        for audio_track_element in audio_element.findall("AudioTrack"):
            audio_track = AudioTrack()
            audio_track.deserialise_xml(audio_track_element)
            self.audio.append(audio_track)

    def is_drop_frame(self):
        """TODO
        """
        frame_rate = self.audio_video_settings.frame_rate
        return False

    def serialize_edl(self, track_index, video=True):
        """
        if video is false then audio is exported instead (TODO)
        """
        frame_rate = self.audio_video_settings.frame_rate

        edl_data = "TITLE: {}\n\n".format(self.name)

        if self.is_drop_frame():
            # TODO
            edl_data += ""
        else:
            edl_data += "FCM: NON-DROP FRAME\n\n\n"

        if video:
            video_track = self.video[track_index]

            for i, visual_object in enumerate(video_track.objects):
                edl_data += "{}\n\n".format(
                    visual_object.serialize_edl(i+1, frame_rate)
                )

        return edl_data

class AudioVideoSettings(EditObject):
    def __init__(self):
        super(AudioVideoSettings, self).__init__()
        self.frame_count = None
        self.audio_sample_rate = None
        self.width = None
        self.height = None
        self.fields = None
        self.par = None
        self.par_custom = None
        self.frame_rate = None

    def _repr_attrs(self):
        attrs = super(AudioVideoSettings, self)._repr_attrs()
        attrs += [
            "frame_count", "audio_sample_rate", "width", "height", "fields", "par", "par_custom", "frame_rate"
        ]
        return attrs

    def deserialise_xml(self, xml_element):

        self.frame_count = int(xml_element.find("FrameCount").text)
        self.audio_sample_rate = int(xml_element.find("AudioSampleRate").text)
        self.width = int(xml_element.find("Width").text)
        self.height = int(xml_element.find("Height").text)
        self.fields = int(xml_element.find("Fields").text)
        self.par = int(xml_element.find("PAR").text)
        self.par_custom = int(xml_element.find("PARCustom").text)
        self.frame_rate = int(xml_element.find("FrameRate").text)

class MediaAsset(HitFilmObject):
    def __init__(self):
        super(MediaAsset, self).__init__()
        self.parent_folder_id = None
        self.filename = None
        self.is_image_sequence = None
        self.override_frame_rate = None
        self.frame_rate = None
        self.override_fields = None
        self.fields = None
        self.override_par = None
        self.par = None
        self.override_alpha = None
        self.alpha_mode = None
        self.in_point = None
        self.out_point = None
        self.instances = []

    def _repr_attrs(self):
        attrs = super(MediaAsset, self)._repr_attrs()
        attrs += [
            "parent_folder_id", "filename", "is_image_sequence", "override_frame_rate", "frame_rate",
            "override_fields", "fields", "override_par", "par", "override_alpha", "alpha_mode",
            "in_point", "out_point",  # "instances"
        ]
        return attrs

    def deserialise_xml(self, xml_element):
        super(MediaAsset, self).deserialise_xml(xml_element)

        self.parent_folder_id = xml_element.find("ParentFolderID").text
        self.filename = xml_element.find("Filename").text
        self.is_image_sequence = int(xml_element.find("IsImageSequence").text)
        self.override_frame_rate = int(xml_element.find("OverrideFrameRate").text)
        self.frame_rate = int(xml_element.find("FrameRate").text)
        self.override_fields = int(xml_element.find("OverrideFields").text)
        self.fields = int(xml_element.find("Fields").text)
        self.override_par = int(xml_element.find("OverridePAR").text)
        self.par = int(xml_element.find("PAR").text)
        self.override_alpha = int(xml_element.find("OverrideAlpha").text)
        self.alpha_mode = int(xml_element.find("AlphaMode").text)
        self.in_point = int(xml_element.find("InPoint").text)
        self.out_point = int(xml_element.find("OutPoint").text)

        self.instances = []  # TODO

        # <Instances>
        #     <Instance ID="f2b183eb-1abf-4a36-ba58-e5b9de9d5d2d" Type="1"/>
        #     <Instance ID="faa7bfb3-ebb8-43a1-8d26-a1adf653888b" Type="0"/>
        #     <Instance ID="53dcceea-a896-4923-955a-29f6ecdbe457" Type="0"/>
        #     <Instance ID="aff8147b-b234-4cf8-a472-35671a0ddece" Type="1"/>
        #     <Instance ID="228a5e4b-1ff1-48e2-b013-633b8299968c" Type="1"/>
        #     <Instance ID="7a2d59dd-1a19-4f65-8e10-f24845cec099" Type="0"/>
        #     <Instance ID="bca3a623-762f-4ed4-a4fa-ce2502c74743" Type="0"/>
        #     <Instance ID="4356b11e-2c23-4f2f-b933-f5fb8b2cfa17" Type="1"/>
        #     <Instance ID="20c3bab8-4a0c-4e51-90fe-58f676234690" Type="0"/>
        #     <Instance ID="cafd1ca6-e96c-4196-8386-2c11642b8ddf" Type="1"/>
        #     <Instance ID="366ba56e-595b-437c-867b-9874e3060bfc" Type="0"/>
        #     <Instance ID="ecd5cee5-2f7c-4b02-8673-cea436ec8027" Type="1"/>
        # </Instances>


class BinFolder(HitFilmObject):
    def __init__(self):
        super(BinFolder, self).__init__()

    def deserialise_xml(self, xml_element):
        super(BinFolder, self).deserialise_xml(xml_element)


class VideoTrack(HitFilmObject):
    def __init__(self):
        super(VideoTrack, self).__init__()
        self.visible = None
        self.objects = []

    def _repr_attrs(self):
        attrs = super(VideoTrack, self)._repr_attrs()
        attrs += [
            "visible", "objects"
        ]
        return attrs

    def deserialise_xml(self, xml_element):
        super(VideoTrack, self).deserialise_xml(xml_element)

        self.visible = int(xml_element.find("Visible").text)

        self.objects = []

        objects_element = xml_element.find("Objects")

        for visual_object_element in objects_element.findall("VisualObject"):
            visual_object = VisualObject()
            visual_object.deserialise_xml(visual_object_element)

            self.objects.append(visual_object)


class SequenceObjectBase(HitFilmObject):
    def __init__(self):
        super(SequenceObjectBase, self).__init__()

        self.sequence_id = None
        self.asset_id = None
        self.asset_type = None
        self.asset_instance_start = None
        self.start_frame = None
        self.end_frame = None
        self.parent_track_id = None
        self.linked_object_id = None
        self.property_manager = None  # TODO

    def _repr_attrs(self):
        attrs = super(SequenceObjectBase, self)._repr_attrs()
        attrs += [
            "sequence_id", "asset_id", "asset_type", "asset_instance_start", "start_frame",
            "end_frame", "parent_track_id", "linked_object_id",
        ]
        return attrs

    def deserialise_xml(self, xml_element):
        super(SequenceObjectBase, self).deserialise_xml(xml_element)

        self.sequence_id = xml_element.find("SequenceID").text
        self.asset_id = xml_element.find("AssetID").text
        self.asset_type = int(xml_element.find("AssetType").text)
        self.asset_instance_start = int(xml_element.find("AssetInstanceStart").text)
        self.start_frame = int(xml_element.find("StartFrame").text)
        self.end_frame = int(xml_element.find("EndFrame").text)
        self.parent_track_id = xml_element.find("ParentTrackID").text
        self.linked_object_id = xml_element.find("LinkedObjectID").text


class VisualObject(SequenceObjectBase):
    def __init__(self):
        super(VisualObject, self).__init__()

        self.blend_mode = None
        self.property_manager = None  # TODO
        # self.effects = None # TODO?

    def _repr_attrs(self):
        attrs = super(VisualObject, self)._repr_attrs()
        attrs += ["blend_mode"]
        return attrs

    def deserialise_xml(self, xml_element):
        super(VisualObject, self).deserialise_xml(xml_element)
        self.blend_mode = int(xml_element.find("BlendMode").text)

        # TODO...
        """
        <PropertyManager Version="1">
            <opacity Spatial="0" Type="0">
                <Default V="3">
                    <fl>100</fl>
                </Default>
            </opacity>
            <rotationZ Spatial="0" Type="1">
                <Default V="3">
                    <fl>0</fl>
                </Default>
            </rotationZ>
            <position Spatial="0" Type="1">
                <Default V="3">
                    <p2 X="0" Y="0"/>
                </Default>
            </position>
            <anchorPoint Spatial="0" Type="1">
                <Default V="3">
                    <p2 X="0" Y="0"/>
                </Default>
            </anchorPoint>
            <speed Spatial="0" Type="1">
                <Default V="3">
                    <db>1</db>
                </Default>
            </speed>
            <scale Spatial="0" Type="1">
                <Default V="3">
                    <sc X="100" Y="100" Z="100"/>
                </Default>
            </scale>
            <scaleLinked Spatial="0" Type="1">
                <Default V="3">
                    <b>1</b>
                </Default>
            </scaleLinked>
        </PropertyManager>
        <Effects/>
        """

    def serialize_edl(self, index, frame_rate, extract_clip_name=True):
        seq_start_timecode = generate_timecode(self.start_frame, frame_rate)
        seq_end_timecode = generate_timecode(self.end_frame, frame_rate)

        duration = self.end_frame - self.start_frame

        src_start_timecode = generate_timecode(self.asset_instance_start, frame_rate)
        src_end_timecode = generate_timecode(self.asset_instance_start+duration, frame_rate)

        if extract_clip_name:
            clip_name = self.name.split(".")[0]
        else:
            clip_name = "{0:03d}".format(index)

        edl_data = "{index} {clip_name} V C {src_start} {src_end} {seq_start} {seq_end}\n".format(
            index="{0:03d}".format(index),
            clip_name=clip_name,
            src_start=format_edl_timecode(*src_start_timecode),
            src_end=format_edl_timecode(*src_end_timecode),
            seq_start=format_edl_timecode(*seq_start_timecode),
            seq_end=format_edl_timecode(*seq_end_timecode),
        )

        edl_data += "\n* FROM CLIP NAME: {}\n".format(self.name)

        return edl_data

class AudioTrack(HitFilmObject):
    def __init__(self):
        super(AudioTrack, self).__init__()
        self.muted = None
        self.level = None
        self.objects = []

    def _repr_attrs(self):
        attrs = super(AudioTrack, self)._repr_attrs()
        attrs += [
            "muted", "level", "objects"
        ]
        return attrs

    def deserialise_xml(self, xml_element):
        super(AudioTrack, self).deserialise_xml(xml_element)

        self.muted = int(xml_element.find("Muted").text)
        self.level = int(xml_element.find("Level").text)
        self.objects = []

        objects_element = xml_element.find("Objects")

        for audio_object_element in objects_element.findall("AudioObject"):
            audio_object = AudioObject()
            audio_object.deserialise_xml(audio_object_element)

            self.objects.append(audio_object)


class AudioObject(SequenceObjectBase):
    def __init__(self):
        super(AudioObject, self).__init__()
        self.muted = None

        # TODO...
        """
        <PropertyManager Version="1">
            <audioLevel Spatial="0" Type="0">
                <Default V="3">
                    <fl>0</fl>
                </Default>
            </audioLevel>
            <speed Spatial="0" Type="1">
                <Default V="3">
                    <db>1</db>
                </Default>
            </speed>
        </PropertyManager>
        """

    def _repr_attrs(self):
        attrs = super(AudioObject, self)._repr_attrs()
        attrs += ["muted"]
        return attrs

    def deserialise_xml(self, xml_element):
        super(AudioObject, self).deserialise_xml(xml_element)
        self.muted = int(xml_element.find("Muted").text)


def inspect_hf_file(filepath):
    with open(filepath, 'r') as f:
        data = f.read()
        dom = minidom.parseString(data)
        pretty_xml = dom.toprettyxml()
        print pretty_xml

    tree = ET.parse(filepath)
    root = tree.getroot()

    project_element = root.find('Project')

    return
    path = [
        # 'BiffProject'
        'Project',
        # 'AssetList',
        'EditorSequence',
        'Video',
        # 'VideoTrack',
        # 'Objects',
    ]

    element = root

    for item in path:
        print item
        element = element.find(item)
        print element
    video_tracks = element.findall('VideoTrack')

    objects = video_tracks[1].find('Objects')
    edits = objects.findall('VisualObject')


def parse_hf_file(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()

    project_element = root.find('Project')

    project = Project()
    project.deserialise_xml(project_element)

    print project

def convert_to_edl(filepath, video_track_index):
    tree = ET.parse(filepath)
    root = tree.getroot()

    project_element = root.find('Project')

    project = Project()
    project.deserialise_xml(project_element)

    edl_data = project.editor_sequence.serialize_edl(video_track_index)

    hf_filename = os.path.basename(filepath)
    hf_dir = os.path.dirname(filepath)

    edl_filename = "{}_videoTrack{}.edl".format(
        hf_filename.split(".")[0],
        video_track_index
    )

    edl_filepath = os.path.join(hf_dir, edl_filename)
    print "Exporting file... {}".format(edl_filepath)

    with open(edl_filepath, 'w') as f:
        f.write(edl_data)

    return edl_data

if __name__ == "__main__":
    # inspect_hf_file(TEST_HF_FILE)
    # parse_hf_file(TEST_HF_FILE)

    convert_to_edl(r"D:\Bands\PablosDog\Gigs\160709_hawesBash\edit\hawesBash030716_003_bck.hfp", 2)

    if False:
        fps = 24
        frame_number = generate_frame_number(90, 33, 50, 10, fps)
        print generate_timecode(frame_number, fps)
