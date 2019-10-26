'''
Created on 2 May 2018

@author: Bren
'''
import os
import subprocess

FFMPEG_DIR = r"F:\Software\ffmpeg\ffmpeg-20180502-e07b191-win64-static\bin"

def rename_file_to_safe(file_path):
    dir = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    safe_filename = filename.replace(" ", "_")
    safe_filepath = os.path.join(dir, safe_filename)
    os.rename(file_path, safe_filepath)
    return safe_filename
    

def video_to_frames(video, output_dir, ext="png", padding=3):
    filename = os.path.basename(video).split(".")[0]
    
    cmd = r"cd /d {} & ".format(FFMPEG_DIR) # the /d is to switch drives
    #output_filename = "{name}_{i:0{width}d}.{ext}".format(name=filename, i=6, width=padding, ext=ext)
    output_filename = r"{name}_%0{width}d.{ext}".format(name=filename, width=padding, ext=ext)
    output = os.path.join(output_dir, output_filename)
    #print output_filename
    
    cmd += r"ffmpeg -i {input} {output}".format(input=video, output=output)
    process = subprocess.Popen(cmd, shell=True)
    #print process.stdout

def videos_to_frames(video_dir, output_dir, ext="png", padding=3, video_ext="mp4", safe_rename=True):
    files = os.listdir(video_dir)
    files = [i for i in files if i.endswith("."+video_ext)]
    
    if safe_rename:
        files = [rename_file_to_safe(os.path.join(video_dir, i)) for i in files]
    
    for filename in files:
        name = filename.split(".")[0]
        file_out_dir = os.path.join(output_dir, name)
        
        if not os.path.exists(file_out_dir):
            os.mkdir(file_out_dir)
        else:
            # :TODO check if it's empty
            pass
        
        video_to_frames(os.path.join(video_dir, filename), file_out_dir, ext=ext, padding=padding)

def get_duplicate_frames(video_input):
    # *** wip ***
    
    cmd = r"cd /d {} & ".format(FFMPEG_DIR) # the /d is to switch drives
    cmd += r"ffmpeg -i {input} -vf mpdecimate -loglevel debug -f null -".format(input=video_input) 
    process = subprocess.Popen(cmd, shell=True)

def renumber_frames(dir):
    filenames = os.listdir(dir)
    width = len(str(len(filenames)))+1
    
    for i, filename in enumerate(filenames):
        filepath = os.path.join(dir, filename)
        
        filename, ext = filename.split(".")
        suffix = filename.split("_")[-1]
        filename = filename[:-len(suffix)]
        filename = "{name}_{i:0{width}}.{ext}".format(name=filename, i=i, width=width, ext=ext)
        new_filepath = os.path.join(dir, filename)
        os.rename(filepath, new_filepath)


#in_dir = r"F:\Jobs\Reel\Material"
#out_dir = r"F:\Jobs\Reel\Material\image_sequences"

in_dir = r"F:\Jobs\Reel\Material\temp3"
out_dir = r"F:\Jobs\Reel\Material\image_sequences1"

#videos_to_frames(in_dir, out_dir, ext="jpg", padding=5, video_ext="webm")

#video_input = r"F:\Jobs\Reel\Material\image_sequences1\4k_30fps_Star_Wars_The_Last_Jedi_-_Kylo_Ren_Meets_With_Supreme_Leader_Snoke\4k_30fps_Star_Wars_The_Last_Jedi_-_Kylo_Ren_Meets_With_Supreme_Leader_Snoke_%05d.jpg" 
#get_duplicate_frames(video_input)

dir = r"F:\Jobs\Reel\Material\image_sequences1\4k_30fps_Star_Wars_The_Last_Jedi_-_Kylo_Ren_Meets_With_Supreme_Leader_Snoke"
renumber_frames(dir)
