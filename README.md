piwall-ffmpeg-scenegenerator
============================

[piwall](http://www.piwall.co.uk/) is videowall software for the raspberry
pi. It is used to project a video over multiple screens.

I wanted to generate a video that projects over all screens but also that 
generated video that would be only shown on one or a few screens.

With this python script you can describe your screen setup and generate videos
for that. It will generate one video file to be sent to the piwall software so
it projects nicely over multiple screens.

You can generate a scene which can consist of multiple audio/video files, to be
shown over one, multiple or all screens.

See description.txt for a description of the various config files.

usage
=====

python ./generate_video.py options [scenename]

options
-------
 -n total scenes to generate at random (not working atm)  
 -o output file (mandatory)  
 -b basepath to videofiles  
 -c path to yaml config files  
 -e actually execute with ffmpeg. With groupscenes the scenes are always generated.  
 -g generate groupscene with name  

 if you only want to generate one scene provide the scenename at the end of all
 options otherwise you have to provide a groupscene(-g groupname).


config files
------------
scenes.yaml  
   Describes the various scenes that can be generated.  
   Contains references to the audio and video files and options for a few
   effects that can be applied (like distortion).

screenconfig.yaml  
   Describe the configuration of the setup of your screens.  
   This includes per screen resolution and position relative to the other 
   screens.

groupsceneconfig.yaml  
   You can describe groupscenes which is a combination of scenes from 
   scenes.yaml. They can have an intro/outro.  
   This just combines multiple scenes into one videofile.
