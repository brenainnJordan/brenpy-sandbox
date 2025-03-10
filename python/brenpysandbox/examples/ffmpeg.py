'''
Created on 2 May 2018

@author: Bren
'''
import os
import subprocess

# FFMPEG_DIR = r"F:\Software\ffmpeg\ffmpeg-20180502-e07b191-win64-static\bin"
FFMPEG_DIR = r"D:\Software\WindowsApps\ffmpeg\ffmpeg-20180502-e07b191-win64-static\bin"

def rename_file_to_safe(file_path):
    dir = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    safe_filename = filename.replace(" ", "_")
    safe_filepath = os.path.join(dir, safe_filename)
    os.rename(file_path, safe_filepath)
    return safe_filename
    

def video_to_frames(video, output_dir, name=None, ext="png", padding=3, switch_drives=True):
    if name is None:
        name = os.path.basename(video).split(".")[0]

    if switch_drives:
        cmd = r"cd /d {} & ".format(FFMPEG_DIR) # the /d is to switch drives
    else:
        cmd = r""

    #output_filename = "{name}_{i:0{width}d}.{ext}".format(name=filename, i=6, width=padding, ext=ext)
    output_filename = r"{name}_%0{width}d.{ext}".format(name=name, width=padding, ext=ext)
    output = os.path.join(output_dir, output_filename)
    #print output_filename
    
    cmd += r"ffmpeg -i {input} {output}".format(input=video, output=output)
    print cmd

    process = subprocess.Popen(cmd, shell=True)
    # print process.stdout

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

def delete_every_other_frame(dir):
    filenames = os.listdir(dir)
    every_other_filename = filenames[::2]

    print "deleting every other frame..."

    for i in every_other_filename[:10]:
        print "   ", i

    for i in every_other_filename:
        filepath = os.path.join(dir, i)
        os.remove(filepath)

    return True


if __name__ == "__main__":
    #in_dir = r"F:\Jobs\Reel\Material"
    #out_dir = r"F:\Jobs\Reel\Material\image_sequences"

    # in_dir = r"F:\Jobs\Reel\Material\temp3"
    # out_dir = r"F:\Jobs\Reel\Material\image_sequences1"

    # videos_to_frames(in_dir, out_dir, ext="jpg", padding=5, video_ext="webm")

    # in_dir = r"E:\Jobs\_Reel\Material\Axis"

    # clip_name = "Deathloop_Official_Cinematic_Reveal_Trailer_E3_2019_1080p60.mp4"
    # clip_name = "Gears_5_Official_Escape_Announcement_Trailer_E3_2019_1080p.mp4"

    # in_dir = os.path.join(in_dir, clip_name)

    # out_dir = r"E:\Jobs\_Reel\Material\Axis\gears_5"
    # video_to_frames(in_dir, out_dir, ext="jpg", name="gears_5", padding=5)

    # out_dir = r"E:\Jobs\_Reel\Material\Axis\Deathloop"
    # video_to_frames(in_dir, out_dir, ext="png", name="deathloop", padding=5, switch_drives=False)

    #video_input = r"F:\Jobs\Reel\Material\image_sequences1\4k_30fps_Star_Wars_The_Last_Jedi_-_Kylo_Ren_Meets_With_Supreme_Leader_Snoke\4k_30fps_Star_Wars_The_Last_Jedi_-_Kylo_Ren_Meets_With_Supreme_Leader_Snoke_%05d.jpg"
    #get_duplicate_frames(video_input)

    # dir = r"F:\Jobs\Reel\Material\image_sequences1\4k_30fps_Star_Wars_The_Last_Jedi_-_Kylo_Ren_Meets_With_Supreme_Leader_Snoke"
    # renumber_frames(dir)

    dir = r"E:\Jobs\_Reel\Material\Axis\deathloop_edit"

    # delete_every_other_frame(dir)
    renumber_frames(dir)
