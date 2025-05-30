'''
* sandbox for experimental ffmpeg scripts *

for more useful utilities put them in bpFfmpegUtils

'''
import os
import subprocess

# FFMPEG_DIR = r"F:\Software\ffmpeg\ffmpeg-20180502-e07b191-win64-static\bin"
FFMPEG_DIR = r"D:\Software\WindowsApps\ffmpeg\ffmpeg-20180502-e07b191-win64-static\bin"



def get_duplicate_frames(video_input):
    # *** wip ***
    
    cmd = r"cd /d {} & ".format(FFMPEG_DIR) # the /d is to switch drives
    cmd += r"ffmpeg -i {input} -vf mpdecimate -loglevel debug -f null -".format(input=video_input) 
    process = subprocess.Popen(cmd, shell=True)


if __name__ == "__main__":
    pass
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
