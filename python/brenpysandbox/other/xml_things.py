'''
Created on Aug 6, 2017

@author: User

useful xml snippets

'''


from dicttoxml import dicttoxml
import xmltodict
from xml.dom import minidom
import xml.etree.ElementTree as ET
import os
import sys
import re
import pprint
import json

def testA():
    test_dict = {
        'thing': 10,
        'blah': {
            'stuff': 'ewthwoei'
        }
    }
    
    xml = dicttoxml(test_dict, custom_root='playlist', attr_type=False)
    print xml
    #return
    dom = minidom.parseString(xml)
    
    print dom.toprettyxml()
    
    try:
        title.decode('utf-8')
    except:
        print title.encode('ascii', 'ignore')
        print title.encode('ascii', 'replace')
    try:
        album.decode('utf-8')
    except:
        print album.encode('ascii', 'ignore')
        #print album.encode('ascii', 'backslashreplace')
            


ML_XSPF = r'C:\Users\User\AppData\Roaming\vlc\ml.xspf'
#ML_XSPF = r'C:\Users\User\AppData\Roaming\vlc\ml_backup.xspf'

ML_OUT = r'C:\Users\User\AppData\Roaming\vlc\ml_test.xspf'

NS ={
    'default': "http://xspf.org/ns/0/",
    'vlc': "http://www.videolan.org/vlc/playlist/ns/0/"
}


# unicode things:
album_test = {
    'thing':{
        'song - & [1]':{
            'title': '& \xf1as \poop',
            'album': '& xf1as [arse'
        }
    },
    'thing2':{
        'song1':{
            'title': 'poop',
            'album': 'arse'
        }
    },
}

def testB():
    tree = ET.parse(ML_XSPF)
    root = tree.getroot()
    
    track_list = root.find('default:trackList', NS)
    nodes = root.find('default:extension', NS)
    
    for track in track_list.findall('default:track', NS):
        print track
        track.find('default:title', NS).text = 'poop'
    
    for node in nodes:
        node.attrib['title'] = 'arse'
    
    ET.dump(root)
    #tree.write(ML_OUT)
    tree.write(
        ML_OUT,
        xml_declaration=True,
        encoding='utf-8',
        method="xml",
        default_namespace=NS['default']
    )


def pretty_xml():
    reel_edit = r'C:\Partition\Jobs\reel\edits\brenReel_007_tempestOnly_005.xml'
    reel_out = r'C:\Partition\Jobs\reel\edits\brenReel_007_tempestOnly_006.xml'
    reel_json = r'C:\Partition\Jobs\reel\edits\brenReel_007_tempestOnly_006.json'
    
    with open(reel_edit, 'r') as f:
        data = f.read()
        dom = minidom.parseString(data)
        pretty_xml = dom.toprettyxml()
        
        tree = ET.parse(reel_edit)
        root = tree.getroot()
        print root.find('Project')
        path = [
            #'BiffProject'
            'Project',
            #'AssetList',
            'EditorSequence',
            'Video',
            #'VideoTrack',
            #'Objects',
        ]
        
        element = root
        
        for item in path:
            print item
            element = element.find(item)
            print element
        video_tracks = element.findall('VideoTrack')
        
        objects = video_tracks[1].find('Objects')
        edits = objects.findall('VisualObject')
        
        data = {}
        rep = {
            'tempest_a1s1.mp4': 'Act 1, Scene 2 | The Tempest | Royal Shakespeare Company.mp4',
            'RSC_tempest_Intel_1080.mp4': '400 years in the making - Intel x The RSC | Experience Amazing | Intel.mp4',
            "tempest_dvd_trailer.mp4": 'The Tempest DVD Trailer | 2017 | Royal Shakespeare Company.mp4',
            
        }
        
        for i, clip in enumerate(edits):
            #print dir(clip.find('Name'))
            name = clip.find('Name').text
            if name in rep:
                name = rep[name]
            
            start = clip.find('StartFrame').text
            end = clip.find('EndFrame').text
            data[i] = {
                '_clip': name,
                'begin': start,
                'end': end
            }
        
        data = json.dumps(
            data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
        
    with open(reel_json, 'w') as f:
        f.write(data)
    
    with open(reel_out, 'w') as f:
        f.write(pretty_xml)
        #data = xmltodict.parse(data)
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(data)

pretty_xml()