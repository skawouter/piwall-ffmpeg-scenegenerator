import random
from video import Video
from audio import Audio
from screens import Screens

class Scene(object):
    def __init__(self, scenecfg, basepath='./', length=1):
        self.videofiles = []
        self.video = Video(scenecfg['video'], basepath, length)
        self.audio = Audio(scenecfg['sound'], basepath, self.video)
        self.length = scenecfg['video']['length']

    def __len__(self):
        return len(self.files)

    def get_video_input_list(self, fixedlength=1):
        return self.video.get_input_list(fixedlength)

    def get_audio_input_list(self):
        return self.audio.get_input_list()

    def generate_complex_video(self, scr):
        cofilter = []
        cofilter.append(' -filter_complex ')
        #generate total screen
        cofilter.append('"color=c=black:size={0}x{1} [base]'.format(
            scr.get_total_width(), scr.get_total_height()))

        v, videocount = self.video.get_video_layers(scr)
        cofilter += v
        cofilter += self.audio.get_audio_layers(self.video.files)
        cofilter.append(' " ')
        return cofilter


    def get_finish_lines(self):
        finishlines = []
        finishlines.append(self.audio.get_finish_line())
        if self.length == 'shortest':
            finishlines.append(' -shortest')
        else:
            finishlines.append(' -t ' + str(self.length))

        finishlines.append(self.audio.get_distort_line())
        finishlines.append(self.video.get_distort_line())

        finishlines.append(' -c:v libx264 -threads 4')

        return finishlines




def generate_scene(scenecfg, screencfg, basepath):
    scr = Screens(screencfg, basepath)
    scene = Scene(scenecfg, basepath, scr.total_screens())
    inputlist = scene.get_video_input_list(scr.total_screens())

    inputstring = ''.join(inputlist)

    #audio inputs
    audioinputs = scene.get_audio_input_list()

    inputstring += ' '.join(audioinputs)
    complexfilter = scene.generate_complex_video(scr)

    endstr = ' '.join(scene.get_finish_lines())
    return inputstring, complexfilter, scene.get_finish_lines()
